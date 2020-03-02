#!/usr/bin/env python3
#############################################################################
### csv2sql.py - Convert CSV to INSERTS for a specified table, with
### control over column names, datatypes, and database systems (dbsystem).
#############################################################################
import sys,os,argparse,re,gzip,csv,logging
#
PROG=os.path.basename(sys.argv[0])
#
#############################################################################
def CsvCheck(fin, dbsystem, noheader, maxchar, delim, qc, keywords):
  csvReader=csv.reader(fin, dialect='excel', delimiter=delim, quotechar=qc) 
  colnames=None; n_in=0; n_err=0;
  for row in csvReader:
    n_in+=1
    if n_in==1 or not colnames:
      if noheader:
        prefix = re.sub(r'\..*$','', os.path.basename(fin.name))
        colnames = ['%s_%d'%(prefix, j) for j in range(1, 1+len(row))]
      else:
        colnames = csvReader.fieldnames[:]
      colnames_clean = CleanNames(colnames, '', keywords)
      DedupNames(colnames_clean)
      for j in range(len(colnames)):
        tag = colnames[j]
        tag_clean = colnames_clean[j]
        logging.debug('column tag %d: %24s%s'%(j+1, tag, (' -> %s'%tag_clean if tag_clean!=tag else '')))
      nval = {colname:0 for colname in colnames}
      maxlen = {colname:0 for colname in colnames}
    for j in range(len(row)):
      val = list(row.values())[j]
      if j<=len(colnames):
        colname = colnames[j]
      else:
        logging.error('[%d] row j_col>len(colnames) %d>%d'%(n_in, j, len(colnames)))
        n_err+=1
      try:
        if type(val) is str:
          val = val.encode('ascii', 'replace')
      except Exception as e:
        logging.error('[%d] %s'%(n_in, str(e)))
        val='%s:ENCODING_ERROR'%PROG
        n_err+=1
      if val.strip(): nval[colname]+=1
      val = EscapeString(val, False, dbsystem)
      maxlen[colname] = max(maxlen[colname], len(val))
      if len(val)>maxchar:
        logging.debug('WARNING: [%d] len>MAX (%d>%d)'%(n_in, len(val), maxchar))
        val=val[:maxchar]
  for j,tag in enumerate(colnames):
    logging.info('%d. "%24s":\tnval = %6d\tmaxlen = %6d'%(j+1, tag, nval[tag], maxlen[tag]))
  logging.info("n_in: %d; n_err: %d"%(n_in, n_err))

#############################################################################
def Csv2Create(fin, fout, dbsystem, dtypes, schema, tablename, colnames, coltypes, prefix, noheader, fixtags, delim, qc, keywords):
  csvReader=csv.DictReader(fin, fieldnames=None, dialect='excel', delimiter=delim, quotechar=qc) 
  if colnames:
    if len(colnames) != len(csvReader.fieldnames):
      logging.error('#colnames)!=#fieldnames (%d!=%d)'%(len(colnames), len(csvReader.fieldnames)))
      return
    csvReader.fieldnames = colnames
  else:
    colnames = csvReader.fieldnames[:]
    if fixtags:
      CleanNames(colnames, prefix, keywords)
      DedupNames(colnames)
  if coltypes:
    if len(coltypes) != len(csvReader.fieldnames):
      logging.error('#coltypes!=#fieldnames (%d!=%d)'%(len(coltypes), len(csvReader.fieldnames)))
      return
    for j in range(len(coltypes)):
      if not coltypes[j]: coltypes[j] = 'CHAR'
  else:
    coltypes = [dtypes['deftype'] for i in range(len(colnames))]
  if dbsystem=='mysql':
    sql='CREATE TABLE %s (\n\t'%(tablename)
  else:
    sql='CREATE TABLE %s.%s (\n\t'%(schema, tablename)
  sql+=(',\n\t'.join(('%s %s'%(colnames[j],dtypes[dbsystem][coltypes[j]])) for j in range(len(colnames))))
  sql+=('\n);')
  if dbsystem=='postgres':
    sql+="\nCOMMENT ON TABLE %s.%s IS 'Created by %s.';"%(schema, tablename, PROG)
  fout.write(sql+'\n')
  logging.info("%s: output SQL CREATE written, columns: %d"%(tablename, len(colnames)))

#############################################################################
def Csv2Insert(fin, fout, dbsystem, dtypes, schema, tablename, colnames, coltypes, prefix, noheader, nullwords, nullify, fixtags, maxchar, chartypes, numtypes, timetypes, delim, qc, keywords, skip, nmax):
  n_in=0; n_out=0; n_err=0;
  csvReader=csv.DictReader(fin, fieldnames=None, dialect='excel', delimiter=delim, quotechar=qc) 
  if colnames:
    if len(colnames) != len(csvReader.fieldnames):
      logging.error('#colnames!=#fieldnames (%d!=%d)'%(len(colnames), len(csvReader.fieldnames)))
      return
    csvReader.fieldnames = colnames
  else:
    colnames = csvReader.fieldnames[:]
    if fixtags:
      CleanNames(colnames, prefix, keywords)
      DedupNames(colnames)
  if coltypes:
    if len(coltypes) != len(csvReader.fieldnames):
      logging.error('#coltypes!=$fieldnames (%d!=%d)'%(len(coltypes), len(csvReader.fieldnames)))
      return
  else:
    coltypes = [dtypes['deftype'] for i in range(len(colnames))]
  for j in range(len(coltypes)):
    if not coltypes[j]: coltypes[j]=dtypes['deftype']
  for row in csvReader:
    n_in+=1
    if n_in<=skip: continue
    if dbsystem=='mysql':
      line = ('INSERT INTO %s (%s) VALUES ('%(tablename, ','.join(colnames)))
    else:
      line = ('INSERT INTO %s.%s (%s) VALUES ('%(schema, tablename, ','.join(colnames)))
    for j,colname in enumerate(csvReader.fieldnames):
      val = str(row[colname])
      #logging.debug("%s: '%s'"%(colname, val))
      if coltypes[j].upper() in chartypes:
        val = EscapeString(str(val), nullify, dbsystem)
        if len(val)>maxchar:
          val = val[:maxchar]
          logging.info('WARNING: [row=%d] string truncated to %d chars: "%s"'%(n_in, maxchar, val))
        val = ("'%s'"%val)
      elif coltypes[j].upper() in numtypes:
        val = 'NULL' if (val.upper() in nullwords or val=='') else ('%s'%val)
      elif coltypes[j].upper() in timetypes:
        val = ("to_timestamp('%s')"%val)
      else:
        logging.error('No type specified or implied: (col=%d)'%(j+1))
        continue
      line+=('%s%s'%((',' if j>0 else ''),val))
    line +=(') ;')
    fout.write(line+'\n')
    n_out+=1
    if n_in==nmax: break
  logging.info("%s: input CSV lines: %d; output SQL inserts: %d"%(tablename, n_in, n_out))

#############################################################################
def CleanName(name, keywords):
  '''Clean table or col name for use without escaping.
1. Downcase.
2. Replace spaces and colons with underscores.
3. Remove punctuation and special chars.
4. Prepend leading numeral.
5. Truncate to 50 chars.
6. Fix if in keyword list, e.g. "procedure".
'''
  name = re.sub(r'[\s:-]+','_',name.lower())
  name = re.sub(r'[^\w]','',name)
  name = re.sub(r'^([\d])',r'col_\1',name)
  name = name[:50]
  if name in keywords:
    name+='_name'
  return name

#############################################################################
def CleanNames(colnames, prefix, keywords):
  for j in range(len(colnames)):
    colnames[j] = CleanName(prefix+colnames[j] if prefix else colnames[j], keywords)
  return colnames

#############################################################################
def DedupNames(colnames):
  unames = set()
  for j in range(len(colnames)):
    if colnames[j] in unames:
      colname_orig = colnames[j]
      k=1
      while colnames[j] in unames:
        k+=1
        colnames[j] = '%s_%d'%(colname_orig, k)
    unames.add(colnames[j])
  return colnames

#############################################################################
def EscapeString(val, nullify, dbsystem):
  val=re.sub(r"'", '', val)
  if dbsystem=='postgres':
    val=re.sub(r'\\', r"'||E'\\\\'||'", val)
  elif dbsystem=='mysql':
    val=re.sub(r'\\', r'\\\\', val)
  if val.strip()=='' and nullify: val='NULL'
  return val

#############################################################################
if __name__=='__main__':
  DBSYSTEMS=['postgres', 'mysql', 'oracle', 'derby']; DBSYSTEM='postgres';
  KEYWORDS='procedure,function,column,table'
  MAXCHAR=1024
  CHARTYPES = 'CHAR,CHARACTER,VARCHAR,TEXT'
  NUMTYPES = 'INT,BIGINT,FLOAT,NUM'
  DEFTYPE='CHAR';
  TIMETYPES = 'DATE,TIMESTAMP'
  NULLWORDS = "NULL,UNSPECIFIED,MISSING,UNKNOWN,NA"
  SCHEMA='public';
  QUOTECHAR='"';

  parser = argparse.ArgumentParser(description="CSV to SQL CREATEs or INSERTs", epilog='')
  ops = [
	"insert", # output INSERT statements
	"create", # output CREATE statements
	"check"] # check input file, profile columns

  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input file (CSV|TSV) [stdin]")
  parser.add_argument("--o", dest="ofile", help="output SQL INSERTs [stdout]")
  parser.add_argument("--schema", default=SCHEMA, help="(Postgres schema, or MySql db)")
  parser.add_argument("--tablename", help="table [convert filename]")
  parser.add_argument("--prefix_tablename", help="prefix + [convert filename]")
  parser.add_argument("--dbsystem", default=DBSYSTEM, help="")
  parser.add_argument("--colnames", help="comma-separated [default: CSV tags]")
  parser.add_argument("--noheader", action="store_true", help="auto-name columns")
  parser.add_argument("--prefix_colnames", help="prefix CSV tags")
  parser.add_argument("--coltypes", help="comma-separated [default: all CHAR]")
  parser.add_argument("--nullify", action="store_true", help="CSV missing CHAR value converts to NULL")
  parser.add_argument("--nullwords", default=NULLWORDS, help="words synonymous with NULL (comma-separated list)")
  parser.add_argument("--keywords", default=KEYWORDS, help="keywords, disallowed tablenames (comma-separated list)")
  parser.add_argument("--char_types", default=CHARTYPES, help="character types (comma-separated list)")
  parser.add_argument("--num_types", default=NUMTYPES, help="numeric types (comma-separated list)")
  parser.add_argument("--time_types", default=TIMETYPES, help="time types (comma-separated list)")
  parser.add_argument("--maxchar", type=int, default=MAXCHAR, help="max string length")
  parser.add_argument("--fixtags", action="store_true", help="tags to colnames (downcase/nopunct/nospace)")
  parser.add_argument("--tsv", action="store_true", help="input file TSV")
  parser.add_argument("--igz", action="store_true", help="input file GZ")
  parser.add_argument("--delim", default=",", help="use if not comma or tab")
  parser.add_argument("--default_type", default=DEFTYPE, help="")
  parser.add_argument("--quotechar", default=QUOTECHAR, help="")
  parser.add_argument("--skip", type=int, default=0, help="skip N records (--insert only)")
  parser.add_argument("--nmax", type=int, default=0, help="max N records (--insert only)")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  if args.tsv: DELIM='\t'
  else: DELIM = args.delim

  NULLWORDS = re.split(r'[\s,]', args.nullwords)
  KEYWORDS = re.split(r'[\s,]', args.keywords)
  CHARTYPES = re.split(r'[\s,]', args.char_types)
  NUMTYPES = re.split(r'[\s,]', args.num_types)
  TIMETYPES = re.split(r'[\s,]', args.time_types)

  if args.ifile:
    fin = gzip.open(args.ifile) if args.igz else open(args.ifile)
  else:
    fin = sys.stdin

  if args.ofile:
    fout = open(args.ofile,'w')
  else:
    fout = sys.stdout

  if args.tablename:
    TABLENAME = args.tablename
  else:
    if not args.ifile: parser.error('--tablename or --i required.')
    TABLENAME = CleanName(args.prefix_tablename+re.sub(r'\..*$','', os.path.basename(args.ifile)), KEYWORDS)
    logging.debug('tablename = "%s"'%TABLENAME)

  DTYPES = {
	'postgres': {
		'CHAR':'VARCHAR(%d)'%args.maxchar,
		'CHARACTER':'VARCHAR(%d)'%args.maxchar,
		'VARCHAR':'VARCHAR(%d)'%args.maxchar,
		'INT':'INTEGER',
		'BIGINT':'BIGINT',
		'FLOAT':'FLOAT',
		'NUM':'FLOAT',
		'BOOL':'BOOLEAN'
		},
	'mysql': {
		'CHAR':'TEXT(%d)'%args.maxchar,
		'CHARACTER':'TEXT(%d)'%args.maxchar,
		'VARCHAR':'TEXT(%d)'%args.maxchar,
		'INT':'INTEGER',
		'BIGINT':'BIGINT',
		'FLOAT':'FLOAT',
		'NUM':'FLOAT',
		'BOOL':'BOOLEAN'
		}
	}
  DTYPES['deftype'] = args.default_type
  

  if args.op=="create":
    Csv2Create(fin, fout, args.dbsystem,
	DTYPES,
	args.schema,
	TABLENAME,
	re.split(r'[,\s]+', args.colnames) if args.colnames else None,
	re.split(r'[,\s]+', args.coltypes) if args.coltypes else None,
	args.prefix_colnames, args.noheader, args.fixtags, DELIM, args.quotechar,
	KEYWORDS)

  elif args.op=="insert":
    Csv2Insert(fin, fout, args.dbsystem,
	DTYPES,
	args.schema,
	TABLENAME,
	re.split(r'[,\s]+', args.colnames) if args.colnames else None,
	re.split(r'[,\s]+', args.coltypes) if args.coltypes else None,
	args.prefix_colnames, args.noheader,
	NULLWORDS, args.nullify, args.fixtags, args.maxchar,
	CHARTYPES, NUMTYPES, TIMETYPES,
	DELIM, args.quotechar, KEYWORDS, args.skip, args.nmax)

  elif args.op=="check":
    CsvCheck(fin, args.dbsystem, args.noheader, args.maxchar, DELIM, args.quotechar, KEYWORDS)

  else:
    parser.error('Invalid operation: %s'%args.op)

