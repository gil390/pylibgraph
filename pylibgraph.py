# -*- coding: utf-8 -*-
import shutil, argparse, graphviz, os, subprocess

# Applications that are mandatory
# None will be replaced by system path to application
APPLICATIONS = {'nm':None}

#=====================================================================
# FUNCTIONS
#=====================================================================

def application_check():
  # Cheks if applications are installed
  mustbeinstalled = []
  for i in APPLICATIONS:
    r = shutil.which(i)
    if r == None:
      mustbeinstalled.append(i)
    else:
      APPLICATIONS[i] = r
  if len(mustbeinstalled) > 0:
    raise Exception(f"Applications that must be installed: {mustbeinstalled}")

def parse_nm_output(fname, arg_stdout, ismain = True):
  # Parsing nm output
  symbol_dic = {}
  a = str(arg_stdout, encoding='utf-8')
  for e in a.split('\n'):
    e2 = e.split()
    if len(e2) == 4 and e2[2] == 'T':
      if ismain:
        symbol_dic[e2[3]] = int(e2[1], base=16)
      else:
        symbol_dic[e2[3]] = [int(e2[1], base=16), fname]

  return symbol_dic

def link_symbols(main_dic, objdic_vector):
  # links symbol from main_dic to object file vector
  link = {}
  for symbol_name in main_dic:

    link[symbol_name] = []
    size = main_dic[symbol_name]

    for objdic in objdic_vector:
      if symbol_name in list(objdic.keys()):
        size2 = objdic[symbol_name][0]
        if size == size2:
          link[symbol_name].append(objdic[symbol_name][1])
  return link

def do_graph(mainbinary, linksymb_list):
  # graphviz graph creation
  dot = graphviz.Digraph(comment=os.path.basename(mainbinary))

  num = 0
  for symbol_key in ls:
    startnum = num

    dot.node(f'A{num}', f'{symbol_key}\n{num}')
    num += 1

    if len(linksymb_list[symbol_key]) == 1:
      obj_file_name = linksymb_list[symbol_key][0]
      fname = os.path.basename(obj_file_name)
      dot.node(f'B{num}', f'{fname}\n{num}')
      dot.edge(f'A{startnum}', f'B{num}')
      num += 1

    elif len(linksymb_list[symbol_key]) > 0:
      dot.node(f'M{startnum}', f'multi\n{startnum}')
      dot.edge(f'A{startnum}', f'M{startnum}')

      for obj_file_name in linksymb_list[symbol_key]:
        fname = os.path.basename(obj_file_name)
        dot.node(f'B{num}', f'{fname}\n{num}')
        dot.edge(f'M{startnum}', f'B{num}')
        num += 1

    else:
      dot.node(f'U{startnum}', f'?')
      dot.edge(f'A{startnum}', f'U{startnum}')

  return dot

#=====================================================================
# MAIN
#=====================================================================
parser = argparse.ArgumentParser(prog="pylibgraph",
  description="python nm symbols grapher")
parser.add_argument('mainbinary', help='main binary to check')
parser.add_argument('objdir', help='parent directory to look for object files')

args = parser.parse_args()

application_check()

# arg verification
if not os.path.isfile(args.mainbinary):
  raise Exception(f'binary {args.mainbinary} must exist')

if not os.path.isdir(args.objdir):
  raise Exception(f'directory {args.objdir} must exist')

# look for object files
obj_files = []
for r, d, f in os.walk(args.objdir):
  for e in f:
    _, ext = os.path.splitext(e)
    if ext.lower() == '.o':
      obj_files.append(os.path.join(r,e))

# nm for main binary
cp = subprocess.run(args=[APPLICATIONS['nm'], '-S', args.mainbinary],
  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if cp.returncode != 0:
  raise Exception(f'nm command failed for {args.mainbinary}\nERROR: {cp.stderr}')
main_dic = parse_nm_output(args.mainbinary, cp.stdout)

# nm for object files
objdic_vector = []
for e in obj_files:
  cp = subprocess.run(args=[APPLICATIONS['nm'], '-S', e],
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if cp.returncode != 0:
    raise Exception(f'nm command failed for {e}\nERROR: {cp.stderr}')
  e_dic = parse_nm_output(e, cp.stdout, ismain = False)
  objdic_vector.append(e_dic)

# link main to objects
ls = link_symbols(main_dic, objdic_vector)

# create graphviz
dot = do_graph(args.mainbinary, ls)

dot.render(f'mainbinary.gv', view=True)
