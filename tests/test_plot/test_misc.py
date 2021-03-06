"""
Tests miscellaneous stuff.

- -s all -i
- -s run_erc,update_xml,run_drc -i
- -s all,run_drc
- -s bogus
- An unknown output type
- -s all and_one_of_two_outs
- Missing schematic
- Wrong PCB name
- Missing PCB
- Missing SCH
- Missing config
- Wrong config name
- Guess the PCB and YAML
- Guess the PCB and YAML when more than one is present
- Guess the SCH and YAML
- Guess the SCH and YAML when more than one is present
- --list
- Create example
  - with PCB
  - already exists
  - Copying
- Load plugin

For debug information use:
pytest-3 --log-cli-level debug
"""

import os
import sys
import shutil
import logging
# Look for the 'utils' module from where the script is running
prev_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if prev_dir not in sys.path:
    sys.path.insert(0, prev_dir)
# Utils import
from utils import context
prev_dir = os.path.dirname(prev_dir)
if prev_dir not in sys.path:
    sys.path.insert(0, prev_dir)
from kibot.misc import (EXIT_BAD_ARGS, EXIT_BAD_CONFIG, NO_PCB_FILE, NO_SCH_FILE, EXAMPLE_CFG, WONT_OVERWRITE, CORRUPTED_PCB,
                        PCBDRAW_ERR, NO_PCBNEW_MODULE, NO_YAML_MODULE)


POS_DIR = 'positiondir'
MK_TARGETS = ['position', 'archive', 'interactive_bom', 'run_erc', '3D', 'kibom_internal', 'drill', 'pcb_render']


def test_skip_pre_and_outputs():
    prj = 'simple_2layer'
    ctx = context.TestContext('SkipPreAndPos', prj, 'pre_and_position', POS_DIR)
    ctx.run(extra=['-s', 'all', '-i'])

    ctx.dont_expect_out_file(ctx.get_pos_both_csv_filename())
    assert ctx.search_err('Skipping all pre-flight actions')
    assert ctx.search_err('Skipping all outputs')

    ctx.clean_up()


def test_skip_pre_and_outputs_2():
    prj = 'simple_2layer'
    ctx = context.TestContext('SkipPreAndPos2', prj, 'pre_and_position', POS_DIR)
    ctx.run(extra=['-s', 'run_erc,update_xml,run_drc', '-i'])

    ctx.dont_expect_out_file(ctx.get_pos_both_csv_filename())
    assert ctx.search_err('Skipping .?run_erc')
    assert ctx.search_err('Skipping .?run_drc')
    assert ctx.search_err('Skipping .?update_xml')
    assert ctx.search_err('Skipping all outputs')

    ctx.clean_up()


def test_skip_pre_and_outputs_3():
    prj = 'simple_2layer'
    ctx = context.TestContext('SkipPreAndPos3', prj, 'pre_and_position', POS_DIR)
    ctx.run(EXIT_BAD_ARGS, extra=['-s', 'all,run_drc'])

    ctx.dont_expect_out_file(ctx.get_pos_both_csv_filename())
    assert ctx.search_err('Use `--skip all`')

    ctx.clean_up()


def test_skip_pre_and_outputs_4():
    prj = 'simple_2layer'
    ctx = context.TestContext('SkipPreAndPos4', prj, 'pre_and_position', POS_DIR)
    ctx.run(EXIT_BAD_ARGS, extra=['-s', 'bogus'])

    ctx.dont_expect_out_file(ctx.get_pos_both_csv_filename())
    assert ctx.search_err('Unknown preflight .?bogus')

    ctx.clean_up()


def test_skip_pre_and_outputs_5():
    prj = 'simple_2layer'
    ctx = context.TestContext('SkipPreAndPos4', prj, 'pre_skip', POS_DIR)
    ctx.run(extra=['-s', 'run_erc,run_drc'])
    assert ctx.search_err('no need to skip')
    ctx.clean_up()


def test_unknown_out():
    prj = 'simple_2layer'
    ctx = context.TestContext('UnknownOut', prj, 'unknown_out', POS_DIR)
    ctx.run(EXIT_BAD_CONFIG)

    ctx.dont_expect_out_file(ctx.get_pos_both_csv_filename())
    assert ctx.search_err("Unknown output type:? .?bogus")

    ctx.clean_up()


def test_select_output():
    prj = '3Rs'
    ctx = context.TestContext('DoASCIISkipCSV', prj, 'pre_and_position', POS_DIR)
    ctx.run(extra=['-s', 'all', 'pos_ascii'])

    ctx.dont_expect_out_file(ctx.get_pos_both_csv_filename())
    ctx.expect_out_file(ctx.get_pos_both_filename())
    assert ctx.search_err('Skipping (.*)position(.*) output')

    ctx.clean_up()


def test_miss_sch():
    prj = 'fail-project'
    ctx = context.TestContext('MissingSCH', prj, 'pre_and_position', POS_DIR)
    ctx.run(EXIT_BAD_ARGS, extra=['pos_ascii'])

    assert ctx.search_err('No SCH file found')

    ctx.clean_up()


def test_miss_sch_2():
    prj = 'fail-project'
    ctx = context.TestContext('MissingSCH_2', prj, 'pre_and_position', POS_DIR)
    ctx.run(NO_SCH_FILE, no_board_file=True, extra=['-e', 'bogus', 'pos_ascii'])

    assert ctx.search_err('Schematic file not found')

    ctx.clean_up()


def test_miss_pcb():
    prj = '3Rs'
    ctx = context.TestContext('MissingPCB', prj, 'pre_and_position', POS_DIR)
    ctx.board_file = 'bogus'
    ctx.run(NO_PCB_FILE, extra=['-s', 'run_erc,update_xml', 'pos_ascii'])

    assert ctx.search_err('Board file not found')

    ctx.clean_up()


def test_miss_pcb_2():
    ctx = context.TestContext('MissingPCB_2', '3Rs', 'pre_and_position', POS_DIR)
    ctx.run(EXIT_BAD_ARGS, no_board_file=True, extra=['-s', 'run_erc,update_xml', 'pos_ascii'])

    assert ctx.search_err('No PCB file found')

    ctx.clean_up()


def test_miss_yaml():
    prj = 'bom'
    ctx = context.TestContext('MissingYaml', prj, 'pre_and_position', POS_DIR)
    ctx.run(EXIT_BAD_ARGS, no_yaml_file=True)

    assert ctx.search_err('No config file')

    ctx.clean_up()


def test_miss_yaml_2():
    prj = '3Rs'
    ctx = context.TestContext('MissingYaml_wrong', prj, 'pre_and_position', POS_DIR)
    ctx.yaml_file = 'bogus'
    ctx.run(EXIT_BAD_ARGS)

    assert ctx.search_err('Plot config file not found: bogus')

    ctx.clean_up()


def test_auto_pcb_and_cfg():
    """ Test guessing the PCB and config file.
        Only one them is there. """
    prj = '3Rs'
    ctx = context.TestContext('GuessPCB_cfg', prj, 'pre_and_position', POS_DIR)

    board_file = os.path.basename(ctx.board_file)
    shutil.copy2(ctx.board_file, ctx.get_out_path(board_file))
    yaml_file = os.path.basename(ctx.yaml_file)
    shutil.copy2(ctx.yaml_file, ctx.get_out_path(yaml_file))

    ctx.run(extra=['-s', 'all', '-i', 'pos_ascii'], no_out_dir=True, no_board_file=True, no_yaml_file=True, chdir_out=True)

    ctx.dont_expect_out_file(ctx.get_pos_both_filename())
    ctx.expect_out_file(ctx.get_pos_both_csv_filename())
    assert ctx.search_out('Using PCB file: '+board_file)
    assert ctx.search_out('Using config file: '+yaml_file)

    ctx.clean_up()


def test_auto_pcb_and_cfg_2():
    """ Test guessing the PCB and config file.
        Two of them are there. """
    prj = '3Rs'
    ctx = context.TestContext('GuessPCB_cfg_rep', prj, 'pre_and_position', POS_DIR)

    board_file = os.path.basename(ctx.board_file)
    shutil.copy2(ctx.board_file, ctx.get_out_path(board_file))
    shutil.copy2(ctx.board_file, ctx.get_out_path('b_'+board_file))
    yaml_file = os.path.basename(ctx.yaml_file)
    shutil.copy2(ctx.yaml_file, ctx.get_out_path(yaml_file))
    shutil.copy2(ctx.yaml_file, ctx.get_out_path('b_'+yaml_file))

    ctx.run(extra=['-s', 'all', '-i', 'pos_ascii'], no_out_dir=True, no_board_file=True, no_yaml_file=True, chdir_out=True)

    assert ctx.search_err('More than one PCB')
    assert ctx.search_err('More than one config')
    m = ctx.search_err('Using (.*).kicad_pcb')
    assert m
    ctx.board_name = m.group(1)

    ctx.dont_expect_out_file(ctx.get_pos_both_filename())
    ctx.expect_out_file(ctx.get_pos_both_csv_filename())

    ctx.clean_up()


def test_auto_pcb_and_cfg_3():
    """ Test guessing the SCH and config file.
        Only one them is there. """
    prj = '3Rs'
    ctx = context.TestContext('GuessSCH_cfg', prj, 'pre_and_position', POS_DIR)

    sch = os.path.basename(ctx.sch_file)
    shutil.copy2(ctx.sch_file, ctx.get_out_path(sch))
    yaml_file = os.path.basename(ctx.yaml_file)
    shutil.copy2(ctx.yaml_file, ctx.get_out_path(yaml_file))

    ctx.run(extra=['-s', 'all', '-i'], no_out_dir=True, no_board_file=True, no_yaml_file=True, chdir_out=True)

    assert ctx.search_out('Using SCH file: '+sch)
    assert ctx.search_out('Using config file: '+yaml_file)

    ctx.clean_up()


def test_auto_pcb_and_cfg_4():
    """ Test guessing the SCH and config file.
        Two SCHs and one PCB.
        The SCH with same name as the PCB should be selected. """
    prj = '3Rs'
    ctx = context.TestContext('GuessSCH_cfg_2', prj, 'pre_and_position', POS_DIR)

    sch = os.path.basename(ctx.sch_file)
    shutil.copy2(ctx.sch_file, ctx.get_out_path(sch))
    shutil.copy2(ctx.sch_file, ctx.get_out_path('b_'+sch))
    brd = os.path.basename(ctx.board_file)
    shutil.copy2(ctx.board_file, ctx.get_out_path(brd))
    yaml_file = os.path.basename(ctx.yaml_file)
    shutil.copy2(ctx.yaml_file, ctx.get_out_path(yaml_file))

    ctx.run(extra=['-s', 'all', '-i'], no_out_dir=True, no_board_file=True, no_yaml_file=True, chdir_out=True)

    assert ctx.search_err('Using '+sch)
    assert ctx.search_out('Using config file: '+yaml_file)

    ctx.clean_up()


def test_auto_pcb_and_cfg_5():
    """ Test guessing the SCH and config file.
        Two SCHs. """
    prj = '3Rs'
    ctx = context.TestContext('GuessSCH_cfg_3', prj, 'pre_and_position', POS_DIR)

    sch = os.path.basename(ctx.sch_file)
    shutil.copy2(ctx.sch_file, ctx.get_out_path(sch))
    shutil.copy2(ctx.sch_file, ctx.get_out_path('b_'+sch))
    yaml_file = os.path.basename(ctx.yaml_file)
    shutil.copy2(ctx.yaml_file, ctx.get_out_path(yaml_file))

    ctx.run(extra=['-s', 'all', '-i'], no_out_dir=True, no_board_file=True, no_yaml_file=True, chdir_out=True)

    assert ctx.search_err('Using (b_)?'+sch)
    assert ctx.search_out('Using config file: '+yaml_file)

    ctx.clean_up()


def test_list():
    ctx = context.TestContext('List', '3Rs', 'pre_and_position', POS_DIR)
    ctx.run(extra=['--list'], no_verbose=True, no_out_dir=True, no_board_file=True)

    assert ctx.search_out('run_erc: True')
    assert ctx.search_out('run_drc: True')
    assert ctx.search_out('update_xml: True')
    assert ctx.search_out(r'Pick and place file.? \(position\) \[position\]')
    assert ctx.search_out(r'Pick and place file.? \(pos_ascii\) \[position\]')

    ctx.clean_up()


def test_help():
    ctx = context.TestContext('Help', '3Rs', 'pre_and_position', POS_DIR)
    ctx.run(extra=['--help'], no_verbose=True, no_out_dir=True, no_yaml_file=True)
    assert ctx.search_out('Usage:')
    assert ctx.search_out('Arguments:')
    assert ctx.search_out('Options:')
    ctx.clean_up()


def test_help_list_outputs():
    ctx = context.TestContext('HelpListOutputs', '3Rs', 'pre_and_position', POS_DIR)
    ctx.run(extra=['--help-list-outputs'], no_verbose=True, no_out_dir=True, no_yaml_file=True, no_board_file=True)
    assert ctx.search_out('Supported outputs:')
    assert ctx.search_out('Gerber format')
    ctx.clean_up()


def test_help_output():
    ctx = context.TestContext('HelpOutput', '3Rs', 'pre_and_position', POS_DIR)
    ctx.run(extra=['--help-output', 'gerber'], no_verbose=True, no_out_dir=True, no_yaml_file=True, no_board_file=True)
    assert ctx.search_out('Gerber format')
    assert ctx.search_out('Type: .?gerber.?')
    ctx.clean_up()


def test_help_output_unk():
    ctx = context.TestContext('HelpOutputUnk', '3Rs', 'pre_and_position', POS_DIR)
    ctx.run(EXIT_BAD_ARGS, extra=['--help-output', 'bogus'], no_verbose=True, no_out_dir=True, no_yaml_file=True,
            no_board_file=True)
    assert ctx.search_err('Unknown output type')
    ctx.clean_up()


def test_help_filters():
    ctx = context.TestContext('test_help_filters', '3Rs', 'pre_and_position', POS_DIR)
    ctx.run(extra=['--help-filters'], no_verbose=True, no_out_dir=True, no_yaml_file=True, no_board_file=True)
    assert ctx.search_out('Generic filter')
    ctx.clean_up()


def test_help_output_plugin_1():
    ctx = context.TestContext('test_help_output_plugin_1', '3Rs', 'pre_and_position', POS_DIR)
    home = os.environ['HOME']
    os.environ['HOME'] = os.path.join(ctx.get_board_dir(), '../..')
    logging.debug('HOME='+os.environ['HOME'])
    try:
        ctx.run(extra=['--help-output', 'test'], no_verbose=True, no_out_dir=True, no_yaml_file=True, no_board_file=True)
    finally:
        os.environ['HOME'] = home
    assert ctx.search_out('Test for plugin')
    assert ctx.search_out('Type: .?test.?')
    assert ctx.search_out('nothing')
    assert ctx.search_out('chocolate')
    ctx.clean_up()


def test_help_output_plugin_2():
    ctx = context.TestContext('test_help_output_plugin_2', '3Rs', 'pre_and_position', POS_DIR)
    home = os.environ['HOME']
    os.environ['HOME'] = os.path.join(ctx.get_board_dir(), '../..')
    logging.debug('HOME='+os.environ['HOME'])
    try:
        ctx.run(extra=['--help-output', 'test2'], no_verbose=True, no_out_dir=True, no_yaml_file=True, no_board_file=True)
    finally:
        os.environ['HOME'] = home
    assert ctx.search_out('Test for plugin')
    assert ctx.search_out('Type: .?test2.?')
    assert ctx.search_out('todo')
    assert ctx.search_out('frutilla')
    ctx.clean_up()


def test_help_outputs():
    ctx = context.TestContext('HelpOutputs', '3Rs', 'pre_and_position', POS_DIR)
    ctx.run(extra=['--help-outputs'], no_verbose=True, no_out_dir=True, no_yaml_file=True, no_board_file=True)
    assert ctx.search_out('Gerber format')
    assert ctx.search_out('Type: .?gerber.?')
    ctx.clean_up()


def test_help_preflights():
    ctx = context.TestContext('HelpPreflights', '3Rs', 'pre_and_position', POS_DIR)
    ctx.run(extra=['--help-preflights'], no_verbose=True, no_out_dir=True, no_yaml_file=True, no_board_file=True)
    assert ctx.search_out('Supported preflight options')
    ctx.clean_up()


def test_example_1():
    """ Example without board """
    ctx = context.TestContext('Example1', '3Rs', 'pre_and_position', '')
    ctx.run(extra=['--example'], no_verbose=True, no_yaml_file=True, no_board_file=True)
    assert ctx.expect_out_file(EXAMPLE_CFG)
    ctx.clean_up()


def test_example_2():
    """ Example with board """
    ctx = context.TestContext('Example2', 'good-project', 'pre_and_position', '')
    ctx.run(extra=['--example'], no_verbose=True, no_yaml_file=True)
    assert ctx.expect_out_file(EXAMPLE_CFG)
    ctx.search_in_file(EXAMPLE_CFG, ['layers: all'])
    ctx.clean_up()


def test_example_3():
    """ Overwrite error """
    ctx = context.TestContext('Example3', 'good-project', 'pre_and_position', '')
    ctx.run(extra=['--example'], no_verbose=True, no_yaml_file=True)
    assert ctx.expect_out_file(EXAMPLE_CFG)
    ctx.run(WONT_OVERWRITE, extra=['--example'], no_verbose=True, no_yaml_file=True)
    ctx.clean_up()


def test_example_4():
    """ Expand copied layers """
    ctx = context.TestContext('Example4', 'good-project', 'pre_and_position', '')
    ctx.run(extra=['--example', '-P'], no_verbose=True, no_yaml_file=True)
    assert ctx.expect_out_file(EXAMPLE_CFG)
    ctx.search_in_file(EXAMPLE_CFG, ['GND.Cu', 'pen_width: 35.0'])
    ctx.search_not_in_file(EXAMPLE_CFG, ['F.Adhes'])
    ctx.clean_up()


def test_example_5():
    """ Copy setting from PCB """
    ctx = context.TestContext('Example5', 'good-project', 'pre_and_position', '')
    output_dir = os.path.join(ctx.output_dir, 'pp')
    ctx.run(extra=['--example', '-p', '-d', output_dir], no_verbose=True, no_yaml_file=True, no_out_dir=True)
    file = os.path.join('pp', EXAMPLE_CFG)
    assert ctx.expect_out_file(file)
    ctx.search_in_file(file, ['layers: selected', 'pen_width: 35.0'])
    ctx.clean_up()


def test_example_6():
    """ Copy setting but no PCB """
    ctx = context.TestContext('Example6', 'good-project', 'pre_and_position', '')
    ctx.run(EXIT_BAD_ARGS, extra=['--example', '-p'], no_verbose=True, no_yaml_file=True, no_board_file=True)
    assert ctx.search_err('no PCB specified')
    ctx.clean_up()


def test_corrupted_pcb():
    prj = 'bom_no_xml'
    ctx = context.TestContext('Corrupted', prj, 'print_pcb', '')
    ctx.run(CORRUPTED_PCB)
    assert ctx.search_err('Error loading PCB file')
    ctx.clean_up()


def test_pcbdraw_fail():
    prj = 'bom'
    ctx = context.TestContext('PcbDrawFail', prj, 'pcbdraw_fail', '')
    ctx.run(PCBDRAW_ERR)
    assert ctx.search_err('Failed to run')
    ctx.clean_up()


# This test was designed for `mcpy`.
# `mcpyrate` can pass it using Python 3.8.6, but seems to have problems on the docker image.
# def test_import_fail():
#     ctx = context.TestContext('test_import_fail', '3Rs', 'pre_and_position', POS_DIR)
#     # Create a read only cache entry that we should delete
#     call(['py3compile', 'kibot/out_any_layer.py'])
#     cache_dir = os.path.join('kibot', '__pycache__')
#     cache_file = glob(os.path.join(cache_dir, 'out_any_layer.*'))[0]
#     os.chmod(cache_file, stat.S_IREAD)
#     os.chmod(cache_dir, stat.S_IREAD | stat.S_IEXEC)
#     try:
#         # mcpyrate: not a problem, for Python 3.8.6
#         ret_code = 0
#         # mcpy:
#         # ret_code = WRONG_INSTALL
#         # Run the command
#         ctx.run(ret_code, extra=['--help-list-outputs'], no_out_dir=True, no_yaml_file=True, no_board_file=True)
#     finally:
#         os.chmod(cache_dir, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)
#         os.remove(cache_file)
#     if False:
#         # mcpy
#         assert ctx.search_err('Wrong installation')
#         assert ctx.search_err('Unable to import plug-ins')
#     ctx.clean_up()
#
#
# def test_import_no_fail():
#     ctx = context.TestContext('test_import_no_fail', '3Rs', 'pre_and_position', POS_DIR)
#     # Create a cache entry that we should delete
#     call(['py3compile', 'kibot/out_any_layer.py'])
#     cache_dir = os.path.join('kibot', '__pycache__')
#     cache_file = glob(os.path.join(cache_dir, 'out_any_layer.*'))[0]
#     try:
#         # Run the command
#         ctx.run(extra=['--help-list-outputs'], no_out_dir=True, no_yaml_file=True, no_board_file=True)
#         if False:
#             # mcpy
#             assert not os.path.isfile(cache_file)
#     finally:
#         if os.path.isfile(cache_file):
#             os.remove(cache_file)
#     ctx.clean_up()


def test_wrong_global_redef():
    ctx = context.TestContext('test_wrong_global_redef', '3Rs', 'pre_and_position', POS_DIR)
    ctx.run(EXIT_BAD_ARGS, extra=['--global-redef', 'bogus'])
    assert ctx.search_err('Malformed global-redef option')
    ctx.clean_up()


def test_no_pcbnew():
    ctx = context.TestContext('test_no_pcbnew', 'bom', 'bom', '')
    cmd = [os.path.abspath(os.path.dirname(os.path.abspath(__file__))+'/force_pcbnew_error.py')]
    ctx.do_run(cmd, NO_PCBNEW_MODULE)
    ctx.search_err('Failed to import pcbnew Python module.')
    ctx.search_err('PYTHONPATH')


def test_old_pcbnew():
    ctx = context.TestContext('test_old_pcbnew', 'bom', 'bom', '')
    cmd = [os.path.abspath(os.path.dirname(os.path.abspath(__file__))+'/force_pcbnew_error.py'), 'fake']
    ctx.do_run(cmd)
    ctx.search_err('Unknown KiCad version, please install KiCad 5.1.6 or newer')


def test_no_yaml():
    ctx = context.TestContext('test_no_yaml', 'bom', 'bom', '')
    cmd = [os.path.abspath(os.path.dirname(os.path.abspath(__file__))+'/force_yaml_error.py')]
    ctx.do_run(cmd, NO_YAML_MODULE)
    ctx.search_err('No yaml module for Python, install python3-yaml')


def test_no_colorama():
    ctx = context.TestContext('test_no_colorama', 'bom', 'bom', '')
    cmd = [os.path.abspath(os.path.dirname(os.path.abspath(__file__))+'/force_colorama_error.py')]
    ctx.do_run(cmd, use_a_tty=True)
    ctx.search_err(r'\[31m.\[1mERROR:Testing 1 2 3')


def check_test_v5_sch_deps(ctx, deps, extra=[]):
    assert len(deps) == 5+len(extra), deps
    dir = os.path.dirname(ctx.board_file)
    deps_abs = [os.path.abspath(f) for f in deps]
    for sch in ['test_v5.sch', 'sub-sheet.sch', 'deeper.sch', 'sub-sheet.sch', 'deeper.sch']:
        assert os.path.abspath(os.path.join(dir, sch)) in deps_abs
    for f in extra:
        assert f in deps


def test_makefile_1():
    prj = 'test_v5'
    ctx = context.TestContext('test_makefile_1', prj, 'makefile_1', '')
    mkfile = ctx.get_out_path('Makefile')
    ctx.run(extra=['-s', 'all', 'archive'])
    ctx.run(extra=['-m', mkfile])
    ctx.expect_out_file('Makefile')
    targets = ctx.read_mk_targets(mkfile)
    all = targets['all']
    phony = targets['.PHONY']
    for target in MK_TARGETS:
        assert target in all
        assert target in phony
        assert target in targets
        logging.debug('- Target `'+target+'` in all, .PHONY and itself OK')
    assert 'kibom_external' not in targets
    # position target
    deps = targets['position'].split(' ')
    assert len(deps) == 2, deps
    assert ctx.get_out_path(os.path.join(POS_DIR, prj+'-top_pos.csv')) in deps
    assert ctx.get_out_path(os.path.join(POS_DIR, prj+'-bottom_pos.csv')) in deps
    assert os.path.abspath(targets[targets['position']]) == ctx.board_file
    logging.debug('- Target `position` OK')
    # interactive_bom target
    deps = targets['interactive_bom'].split(' ')
    assert len(deps) == 1, deps
    assert ctx.get_out_path(os.path.join('ibom', prj+'-ibom.html')) in deps
    assert os.path.abspath(targets[targets['interactive_bom']]) == ctx.board_file
    logging.debug('- Target `interactive_bom` OK')
    # pcb_render target
    deps = targets['pcb_render'].split(' ')
    assert len(deps) == 1, deps
    assert ctx.get_out_path(prj+'-top.svg') in deps
    assert os.path.abspath(targets[targets['pcb_render']]) == ctx.board_file
    logging.debug('- Target `pcb_render` OK')
    # drill target
    deps = targets['drill'].split(' ')
    assert len(deps) == 3, deps
    assert ctx.get_out_path(os.path.join('gerbers', prj+'-drill.drl')) in deps
    assert ctx.get_out_path(os.path.join('gerbers', prj+'-drill_report.txt')) in deps
    assert ctx.get_out_path(os.path.join('gerbers', prj+'-drill_map.pdf')) in deps
    assert os.path.abspath(targets[targets['drill']]) == ctx.board_file
    logging.debug('- Target `drill` OK')
    # run_erc target
    deps = targets['run_erc'].split(' ')
    assert len(deps) == 1, deps
    assert ctx.get_out_path(prj+'-erc.txt') in deps
    check_test_v5_sch_deps(ctx, targets[targets['run_erc']].split(' '))
    logging.debug('- Target `run_erc` OK')
    # 3D target
    deps = targets['3D'].split(' ')
    assert len(deps) == 1, deps
    assert ctx.get_out_path(os.path.join('3D', prj+'-3D.step')) in deps
    deps = targets[targets['3D']].split(' ')
    assert os.path.relpath(ctx.board_file) in deps
    # We can't check the WRL because it isn't included in the docker image
    logging.debug('- Target `3D` OK')
    # kibom_internal target
    deps = targets['kibom_internal'].split(' ')
    assert len(deps) == 1, deps
    assert ctx.get_out_path(os.path.join('BoM', prj+'-bom.html')) in deps
    check_test_v5_sch_deps(ctx, targets[targets['kibom_internal']].split(' '), [ctx.get_out_path('config.kibom.ini')])
    logging.debug('- Target `kibom_internal` OK')
    # archive target
    deps = targets['archive'].split(' ')
    assert len(deps) == 1, deps
    assert ctx.get_out_path(prj+'-archive.zip') in deps
    deps = targets[targets['archive']].split(' ')
    assert len(deps) == 12, deps
    assert 'position' in deps
    assert 'interactive_bom' in deps
    assert '3D' in deps
    assert 'drill' in deps
    assert ctx.get_out_path('error.txt') in deps
    assert ctx.get_out_path('output.txt') in deps
    assert ctx.get_out_path('Makefile') in deps
    assert ctx.get_out_path('config.kibom.ini') in deps
    assert ctx.get_out_path('positiondir') in deps
    assert ctx.get_out_path('ibom') in deps
    assert ctx.get_out_path('3D') in deps
    assert ctx.get_out_path('gerbers') in deps
    logging.debug('- Target `archive` OK')
    ctx.search_err(r'\(kibom_external\) \[kibom\] uses a name generated by the external tool')
    ctx.clean_up()


def test_empty_zip():
    prj = 'test_v5'
    ctx = context.TestContext('test_empty_zip', prj, 'empty_zip', '')
    ctx.run()
    ctx.expect_out_file(prj+'-result.zip')
    ctx.search_err('No files provided, creating an empty archive')
    ctx.clean_up()
