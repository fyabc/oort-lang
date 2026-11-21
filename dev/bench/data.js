window.BENCHMARK_DATA = {
  "lastUpdate": 1795232209352,
  "repoUrl": "https://github.com/fyabc/oort-lang.py",
  "entries": {
    "Benchmark": [
      {
        "commit": {
          "author": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "committer": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "distinct": true,
          "id": "0098c1783d1d35449b7b00bb81556533009795e0",
          "message": "ci: keep the benchmark workflow on the history branch\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-19T07:08:58+08:00",
          "tree_id": "900fe30c49d038c10677a1135f5ea61222b345f9",
          "url": "https://github.com/fyabc/oort-lang.py/commit/0098c1783d1d35449b7b00bb81556533009795e0"
        },
        "date": 1795043368145,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 27.016233155250944,
            "unit": "iter/sec",
            "range": "stddev: 0.003808035823624118",
            "extra": "mean: 37.01478271428219 msec\nrounds: 7"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.9286621238526944,
            "unit": "iter/sec",
            "range": "stddev: 0.008684021822855013",
            "extra": "mean: 518.494135200001 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 126.38304936511082,
            "unit": "iter/sec",
            "range": "stddev: 0.0002884431441083922",
            "extra": "mean: 7.912453489795753 msec\nrounds: 98"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 114.91352193492618,
            "unit": "iter/sec",
            "range": "stddev: 0.0012227514742590866",
            "extra": "mean: 8.702196078946088 msec\nrounds: 114"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 45.843765720295096,
            "unit": "iter/sec",
            "range": "stddev: 0.0006867089720850887",
            "extra": "mean: 21.813216787234794 msec\nrounds: 47"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 36499.07109115412,
            "unit": "iter/sec",
            "range": "stddev: 0.000002431160571989017",
            "extra": "mean: 27.397957539866244 usec\nrounds: 19171"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 34963.56084851509,
            "unit": "iter/sec",
            "range": "stddev: 0.0000024508876940539235",
            "extra": "mean: 28.601205819185616 usec\nrounds: 16670"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 53887.69170011043,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020166084841516483",
            "extra": "mean: 18.557113293423008 usec\nrounds: 16241"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 32873.17509681786,
            "unit": "iter/sec",
            "range": "stddev: 0.000007687031364354459",
            "extra": "mean: 30.41993957245707 usec\nrounds: 13752"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 70823.95015890386,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015446365320754592",
            "extra": "mean: 14.119517447930455 usec\nrounds: 26708"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 70091.64216742631,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015758903641043267",
            "extra": "mean: 14.267036255354423 usec\nrounds: 20549"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 31055.003629593557,
            "unit": "iter/sec",
            "range": "stddev: 0.000007136886279918227",
            "extra": "mean: 32.20093006355536 usec\nrounds: 11868"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 28359.925122207,
            "unit": "iter/sec",
            "range": "stddev: 0.000008326606531615136",
            "extra": "mean: 35.26102398687077 usec\nrounds: 12590"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 6721.742100033236,
            "unit": "iter/sec",
            "range": "stddev: 0.00002821001532257228",
            "extra": "mean: 148.770956266688 usec\nrounds: 3407"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 2093.9651884509685,
            "unit": "iter/sec",
            "range": "stddev: 0.00009057332205188951",
            "extra": "mean: 477.5628580242826 usec\nrounds: 1296"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 9553.695684183807,
            "unit": "iter/sec",
            "range": "stddev: 0.00029152372883019977",
            "extra": "mean: 104.6715358178621 usec\nrounds: 9632"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "committer": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "distinct": true,
          "id": "d210d446367dbb36b5015874a881bd007e91c1b6",
          "message": "feat: implement module loading and import keyword highlighting\n\n- Add the .ort module loader with relative/bare path resolution, canonical\n  path caching, eager hoisted initialization and circular-import diagnostics.\n- Isolate each module's global environment; resolve globals against the\n  defining module and expose read-only module namespaces with re-export.\n- Add -I/--module-path, pair diagnostics with their source inputs, and keep\n  imported-module errors attached to the module file and line.\n- Add spec 07, OP 0006 research/decisions, a multi-file example, and unit,\n  CLI, REPL and example tests.\n- Bump the VSCode extension to 0.1.1 and scope import/from/as as\n  keyword.control.import.oort with grammar tests.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-19T08:08:34+08:00",
          "tree_id": "919b37332d457f7026b96392600612222895e4c8",
          "url": "https://github.com/fyabc/oort-lang.py/commit/d210d446367dbb36b5015874a881bd007e91c1b6"
        },
        "date": 1795046989411,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 22.479563555812796,
            "unit": "iter/sec",
            "range": "stddev: 0.005420294187910256",
            "extra": "mean: 44.48484942855657 msec\nrounds: 7"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.6862767249499255,
            "unit": "iter/sec",
            "range": "stddev: 0.007329288027320708",
            "extra": "mean: 593.0224768000016 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 96.70913808607439,
            "unit": "iter/sec",
            "range": "stddev: 0.00023861837417647888",
            "extra": "mean: 10.340284483871278 msec\nrounds: 93"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 103.43930271659175,
            "unit": "iter/sec",
            "range": "stddev: 0.0015567354265411412",
            "extra": "mean: 9.667505229998028 msec\nrounds: 100"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 41.7635891017568,
            "unit": "iter/sec",
            "range": "stddev: 0.0002321092526357802",
            "extra": "mean: 23.944302238093194 msec\nrounds: 42"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 36029.96559043276,
            "unit": "iter/sec",
            "range": "stddev: 0.000002267201055980605",
            "extra": "mean: 27.75467541011296 usec\nrounds: 15136"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 31498.66028855332,
            "unit": "iter/sec",
            "range": "stddev: 0.0000031963332237441016",
            "extra": "mean: 31.747381978763148 usec\nrounds: 13129"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 47189.75358937668,
            "unit": "iter/sec",
            "range": "stddev: 0.000002583443603956502",
            "extra": "mean: 21.19104093446928 usec\nrounds: 10700"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 28012.234196726808,
            "unit": "iter/sec",
            "range": "stddev: 0.0001676892577947669",
            "extra": "mean: 35.69868768685536 usec\nrounds: 10704"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 67038.60633809488,
            "unit": "iter/sec",
            "range": "stddev: 0.000001713958750827581",
            "extra": "mean: 14.916777878059008 usec\nrounds: 19953"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 61020.56223963438,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018059258601292578",
            "extra": "mean: 16.38791848676994 usec\nrounds: 15887"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 25244.35404626551,
            "unit": "iter/sec",
            "range": "stddev: 0.00001350324953698635",
            "extra": "mean: 39.612817906423466 usec\nrounds: 9896"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 25508.515709372605,
            "unit": "iter/sec",
            "range": "stddev: 0.000009617259769154302",
            "extra": "mean: 39.20259459207065 usec\nrounds: 10059"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 5557.49251995208,
            "unit": "iter/sec",
            "range": "stddev: 0.000032836632573704174",
            "extra": "mean: 179.9372642266053 usec\nrounds: 2759"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1676.2416901426338,
            "unit": "iter/sec",
            "range": "stddev: 0.0007306526402897798",
            "extra": "mean: 596.5726815414719 usec\nrounds: 986"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 8529.448966986023,
            "unit": "iter/sec",
            "range": "stddev: 0.0003512685332997103",
            "extra": "mean: 117.2408679471074 usec\nrounds: 10049"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "committer": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "distinct": true,
          "id": "48f699713b33edc216db8f47d95edad04847bd99",
          "message": "feat: add minimal standard library and host boundary\n\n- Add eager map/filter/zip/enumerate builtins and stable sorted with Oort\n  operator comparison.\n- Add native math and string modules behind a closed standard-library\n  registry, importable as bare module names.\n- Introduce HostBridge, HOST/VALUE/CONTEXT native call modes and\n  NativeContext so native functions can call Oort callables.\n- Rename py_value to host_value, make container projection alias/cycle aware,\n  and make len read Oort containers without host projection.\n- Add spec 08, OP 0012, host-boundary design notes, stdlib examples, tests,\n  benchmarks and the installed-wheel standard-library smoke test.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-20T02:45:27+08:00",
          "tree_id": "a43b8b9aaa3d901ac69473d02a3bfbea6c9c9a04",
          "url": "https://github.com/fyabc/oort-lang.py/commit/48f699713b33edc216db8f47d95edad04847bd99"
        },
        "date": 1795113966562,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 26.71471602205056,
            "unit": "iter/sec",
            "range": "stddev: 0.004372734485763497",
            "extra": "mean: 37.43255212500074 msec\nrounds: 8"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.964760815003939,
            "unit": "iter/sec",
            "range": "stddev: 0.009216542283045597",
            "extra": "mean: 337.2953375999984 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 109.11017846038256,
            "unit": "iter/sec",
            "range": "stddev: 0.0006714925429309657",
            "extra": "mean: 9.16504779032229 msec\nrounds: 124"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 176.51072776478986,
            "unit": "iter/sec",
            "range": "stddev: 0.0012424110799336928",
            "extra": "mean: 5.6653780348838305 msec\nrounds: 172"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 76.0547244925157,
            "unit": "iter/sec",
            "range": "stddev: 0.001265684761256248",
            "extra": "mean: 13.148427092105328 msec\nrounds: 76"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 60623.38279886098,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011587492852218332",
            "extra": "mean: 16.49528538052463 usec\nrounds: 26964"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 57481.75462598073,
            "unit": "iter/sec",
            "range": "stddev: 0.0000046540810411791316",
            "extra": "mean: 17.3968245490547 usec\nrounds: 21345"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 92575.79575874915,
            "unit": "iter/sec",
            "range": "stddev: 0.0000030111741973997737",
            "extra": "mean: 10.801959538171099 usec\nrounds: 19055"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 60599.07675730076,
            "unit": "iter/sec",
            "range": "stddev: 0.000007909616349792935",
            "extra": "mean: 16.501901571949666 usec\nrounds: 16540"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 126865.51690273543,
            "unit": "iter/sec",
            "range": "stddev: 7.502348686846098e-7",
            "extra": "mean: 7.882362555355956 usec\nrounds: 29350"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 118248.00144240195,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012743466415039468",
            "extra": "mean: 8.456802548896315 usec\nrounds: 22912"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 58177.87429504775,
            "unit": "iter/sec",
            "range": "stddev: 0.000004569075786320439",
            "extra": "mean: 17.18866514318696 usec\nrounds: 14003"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 49563.495605283504,
            "unit": "iter/sec",
            "range": "stddev: 0.0001283587410749979",
            "extra": "mean: 20.17613947094965 usec\nrounds: 16369"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 9707.438569932914,
            "unit": "iter/sec",
            "range": "stddev: 0.000019519912400964633",
            "extra": "mean: 103.0137860565324 usec\nrounds: 4174"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 2922.8723721508672,
            "unit": "iter/sec",
            "range": "stddev: 0.00005170582602825947",
            "extra": "mean: 342.12920465772015 usec\nrounds: 1417"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 13508.746488086146,
            "unit": "iter/sec",
            "range": "stddev: 0.00034592008116814127",
            "extra": "mean: 74.02611344301533 usec\nrounds: 16105"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 139.78295081305995,
            "unit": "iter/sec",
            "range": "stddev: 0.0018517861256071376",
            "extra": "mean: 7.153948276119593 msec\nrounds: 134"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 107.49400691453941,
            "unit": "iter/sec",
            "range": "stddev: 0.00015363031436673648",
            "extra": "mean: 9.302844211538478 msec\nrounds: 104"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 1159.7893640722875,
            "unit": "iter/sec",
            "range": "stddev: 0.000027357651736246415",
            "extra": "mean: 862.2255307539376 usec\nrounds: 1008"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 375.82877382796585,
            "unit": "iter/sec",
            "range": "stddev: 0.002784245246112292",
            "extra": "mean: 2.660786160183004 msec\nrounds: 437"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 140.62236896097593,
            "unit": "iter/sec",
            "range": "stddev: 0.0020511343423133665",
            "extra": "mean: 7.111244159721913 msec\nrounds: 144"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 1145.9747894831644,
            "unit": "iter/sec",
            "range": "stddev: 0.0010750008957623085",
            "extra": "mean: 872.6195455407887 usec\nrounds: 1054"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 401.45657711830745,
            "unit": "iter/sec",
            "range": "stddev: 0.0026701739989844217",
            "extra": "mean: 2.4909294229978567 msec\nrounds: 487"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "committer": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "distinct": true,
          "id": "eae7f18b1d5c8fe44b1822cd0734ccdc1cf98c30",
          "message": "feat: add user-defined iterator protocol\n\n- Add __iter__ protocol returning a callable iterator that yields\n  (value, valid) tuples with a strict Bool flag.\n- Stream for loops through open_iterator/iterator_next instead of\n  snapshotting all items first, supporting infinite iterators and break.\n- Add a native Iterator type with a fast next_value path; builtin\n  containers implement __iter__ so the interpreter no longer dispatches\n  on container types.\n- Let eager collection helpers accept finite user iterables.\n- Add iterator tests, examples, benchmarks, OP 0013 and spec 09.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-20T03:16:35+08:00",
          "tree_id": "3e4ae93b70e5c3662054f25975be36e19e417d36",
          "url": "https://github.com/fyabc/oort-lang.py/commit/eae7f18b1d5c8fe44b1822cd0734ccdc1cf98c30"
        },
        "date": 1795115838014,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 23.965474785818298,
            "unit": "iter/sec",
            "range": "stddev: 0.005235357158976864",
            "extra": "mean: 41.72669262499884 msec\nrounds: 8"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.8291674704284344,
            "unit": "iter/sec",
            "range": "stddev: 0.003853303052524342",
            "extra": "mean: 353.4608715999994 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 165.04048586019178,
            "unit": "iter/sec",
            "range": "stddev: 0.001126726544973743",
            "extra": "mean: 6.059119341463371 msec\nrounds: 164"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 46.84640493612773,
            "unit": "iter/sec",
            "range": "stddev: 0.004194625619606788",
            "extra": "mean: 21.34635520833328 msec\nrounds: 48"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 77.54215928187413,
            "unit": "iter/sec",
            "range": "stddev: 0.002004122667197071",
            "extra": "mean: 12.896210387498908 msec\nrounds: 80"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 107.02844531972752,
            "unit": "iter/sec",
            "range": "stddev: 0.00019789025701312738",
            "extra": "mean: 9.343310528455183 msec\nrounds: 123"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 161.83324589754662,
            "unit": "iter/sec",
            "range": "stddev: 0.0017345624561689997",
            "extra": "mean: 6.179200042944698 msec\nrounds: 163"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 69.53106387293226,
            "unit": "iter/sec",
            "range": "stddev: 0.0009666367067192574",
            "extra": "mean: 14.382060971014276 msec\nrounds: 69"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 55299.93039978612,
            "unit": "iter/sec",
            "range": "stddev: 0.000006643525711059596",
            "extra": "mean: 18.083205399547257 usec\nrounds: 18335"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 53620.347618213214,
            "unit": "iter/sec",
            "range": "stddev: 0.000002342684683842649",
            "extra": "mean: 18.649636647643256 usec\nrounds: 16967"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 85519.79265840391,
            "unit": "iter/sec",
            "range": "stddev: 0.000007642890231971792",
            "extra": "mean: 11.6931995379637 usec\nrounds: 15150"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 57316.66573682351,
            "unit": "iter/sec",
            "range": "stddev: 0.000007088504253108327",
            "extra": "mean: 17.446932530786466 usec\nrounds: 11546"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 102050.84141926664,
            "unit": "iter/sec",
            "range": "stddev: 0.000010910549833192497",
            "extra": "mean: 9.799037284676475 usec\nrounds: 26472"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 109988.07249747154,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017745908591723755",
            "extra": "mean: 9.091894941817337 usec\nrounds: 23368"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 54139.363068973515,
            "unit": "iter/sec",
            "range": "stddev: 0.000004738040156477451",
            "extra": "mean: 18.470848996246975 usec\nrounds: 13748"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 47877.164575869014,
            "unit": "iter/sec",
            "range": "stddev: 0.000005777664508780633",
            "extra": "mean: 20.886784103835982 usec\nrounds: 13173"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 9423.50413365391,
            "unit": "iter/sec",
            "range": "stddev: 0.000020135986723597455",
            "extra": "mean: 106.11763796322077 usec\nrounds: 3751"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 2325.6503343504005,
            "unit": "iter/sec",
            "range": "stddev: 0.0012609082210315904",
            "extra": "mean: 429.9872535564636 usec\nrounds: 1195"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 12051.867108792467,
            "unit": "iter/sec",
            "range": "stddev: 0.0005349215130135636",
            "extra": "mean: 82.97469520473287 usec\nrounds: 13701"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 126.82871460105035,
            "unit": "iter/sec",
            "range": "stddev: 0.004551301552838059",
            "extra": "mean: 7.88464980620184 msec\nrounds: 129"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 94.48426544420244,
            "unit": "iter/sec",
            "range": "stddev: 0.0038904908254172466",
            "extra": "mean: 10.583772814432779 msec\nrounds: 97"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 1064.3105824006398,
            "unit": "iter/sec",
            "range": "stddev: 0.000051870863128993425",
            "extra": "mean: 939.5753613051728 usec\nrounds: 858"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 191.96164191059827,
            "unit": "iter/sec",
            "range": "stddev: 0.010796861073633897",
            "extra": "mean: 5.209374071022621 msec\nrounds: 352"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 140.44661426695095,
            "unit": "iter/sec",
            "range": "stddev: 0.003325098287465492",
            "extra": "mean: 7.120143160583928 msec\nrounds: 137"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 986.7401271932721,
            "unit": "iter/sec",
            "range": "stddev: 0.0025379397205043774",
            "extra": "mean: 1.013438059770048 msec\nrounds: 870"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 258.62409540028494,
            "unit": "iter/sec",
            "range": "stddev: 0.007808126070495698",
            "extra": "mean: 3.866615747663619 msec\nrounds: 428"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "committer": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "distinct": true,
          "id": "7d3f028a2bde0091194a78a208b3fab4930303d6",
          "message": "docs: document extension methods and add example\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-20T03:53:26+08:00",
          "tree_id": "c04a04b23818cabebc94c9db5d99d20ee7223346",
          "url": "https://github.com/fyabc/oort-lang.py/commit/7d3f028a2bde0091194a78a208b3fab4930303d6"
        },
        "date": 1795118209785,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 19.785673277080082,
            "unit": "iter/sec",
            "range": "stddev: 0.008787921236848139",
            "extra": "mean: 50.541620999999516 msec\nrounds: 6"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.0858757638461434,
            "unit": "iter/sec",
            "range": "stddev: 0.007417161167667603",
            "extra": "mean: 479.4149379999993 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 33.29589115707871,
            "unit": "iter/sec",
            "range": "stddev: 0.00019727731683801211",
            "extra": "mean: 30.03373585294172 msec\nrounds: 34"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 31.409725324150887,
            "unit": "iter/sec",
            "range": "stddev: 0.0004283139560787989",
            "extra": "mean: 31.837272999999833 msec\nrounds: 32"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 30.194422186402935,
            "unit": "iter/sec",
            "range": "stddev: 0.00041806567802315044",
            "extra": "mean: 33.11869966666615 msec\nrounds: 30"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 113.59124572324251,
            "unit": "iter/sec",
            "range": "stddev: 0.002392803483897169",
            "extra": "mean: 8.803495318965277 msec\nrounds: 116"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 36.16189137617029,
            "unit": "iter/sec",
            "range": "stddev: 0.00021440453034496336",
            "extra": "mean: 27.65342082352952 msec\nrounds: 34"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 56.64138014069695,
            "unit": "iter/sec",
            "range": "stddev: 0.0002112310546580697",
            "extra": "mean: 17.65493703571495 msec\nrounds: 56"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 90.44234669421128,
            "unit": "iter/sec",
            "range": "stddev: 0.0005133436220535561",
            "extra": "mean: 11.056767504950251 msec\nrounds: 101"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 112.11927698779142,
            "unit": "iter/sec",
            "range": "stddev: 0.0031907641065027767",
            "extra": "mean: 8.919072855855903 msec\nrounds: 111"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 48.07596948861622,
            "unit": "iter/sec",
            "range": "stddev: 0.002874153050071718",
            "extra": "mean: 20.80041256862823 msec\nrounds: 51"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 41408.795467733275,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018124424389073032",
            "extra": "mean: 24.149458797448574 usec\nrounds: 11759"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 40105.9106111048,
            "unit": "iter/sec",
            "range": "stddev: 0.000001935725918242873",
            "extra": "mean: 24.933980671744504 usec\nrounds: 15004"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 62548.66757074196,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015545966573972751",
            "extra": "mean: 15.987550795850435 usec\nrounds: 10365"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 42877.51105997991,
            "unit": "iter/sec",
            "range": "stddev: 0.00000776700427166163",
            "extra": "mean: 23.322249246257172 usec\nrounds: 9950"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 84433.2669130848,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013302856129067084",
            "extra": "mean: 11.843672956885527 usec\nrounds: 18759"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 79217.41671341822,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013092569100198854",
            "extra": "mean: 12.623486620595836 usec\nrounds: 18536"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 40450.971209275,
            "unit": "iter/sec",
            "range": "stddev: 0.000006116809162344036",
            "extra": "mean: 24.721285301815204 usec\nrounds: 7967"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 37011.88630908388,
            "unit": "iter/sec",
            "range": "stddev: 0.000008225846249398994",
            "extra": "mean: 27.018347339799554 usec\nrounds: 10638"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 8224.52610459345,
            "unit": "iter/sec",
            "range": "stddev: 0.000027165009327307618",
            "extra": "mean: 121.58755255716116 usec\nrounds: 3187"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1765.7757864745922,
            "unit": "iter/sec",
            "range": "stddev: 0.0011006134085206553",
            "extra": "mean: 566.3233167312372 usec\nrounds: 1285"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 9146.646867482505,
            "unit": "iter/sec",
            "range": "stddev: 0.0006511015113586641",
            "extra": "mean: 109.32968272287056 usec\nrounds: 11003"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 94.9249884490181,
            "unit": "iter/sec",
            "range": "stddev: 0.004923760832662226",
            "extra": "mean: 10.53463388659853 msec\nrounds: 97"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 70.69546170425664,
            "unit": "iter/sec",
            "range": "stddev: 0.004436915795838838",
            "extra": "mean: 14.145179561643474 msec\nrounds: 73"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 782.124308116371,
            "unit": "iter/sec",
            "range": "stddev: 0.00003724834350573772",
            "extra": "mean: 1.2785691348838777 msec\nrounds: 645"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 163.87368294073605,
            "unit": "iter/sec",
            "range": "stddev: 0.010482401041544695",
            "extra": "mean: 6.102261095588143 msec\nrounds: 272"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 98.22985176287348,
            "unit": "iter/sec",
            "range": "stddev: 0.003967887974719501",
            "extra": "mean: 10.1802047142858 msec\nrounds: 98"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 683.0309227643287,
            "unit": "iter/sec",
            "range": "stddev: 0.0030879903824289957",
            "extra": "mean: 1.4640625580359523 msec\nrounds: 672"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 189.3503179788561,
            "unit": "iter/sec",
            "range": "stddev: 0.009432010334189493",
            "extra": "mean: 5.281216375415147 msec\nrounds: 301"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "committer": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "distinct": true,
          "id": "0cfe53a6aeee2cdccc393682dc114bf70dca0b8d",
          "message": "feat: interrupt running REPL statements and add exit commands\n\nCtrl-C now interrupts an executing statement and returns to the prompt, and\nbare exit/quit close the REPL when no multi-line input is pending.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-20T04:11:04+08:00",
          "tree_id": "08871d6b81814fa0d2daa1029dbaed135e1cdb79",
          "url": "https://github.com/fyabc/oort-lang.py/commit/0cfe53a6aeee2cdccc393682dc114bf70dca0b8d"
        },
        "date": 1795119761150,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 17.14368313530698,
            "unit": "iter/sec",
            "range": "stddev: 0.005044668295019305",
            "extra": "mean: 58.33052280000004 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.6458444320646892,
            "unit": "iter/sec",
            "range": "stddev: 0.002653357246289674",
            "extra": "mean: 607.5908393999996 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 25.48925445039538,
            "unit": "iter/sec",
            "range": "stddev: 0.001251903149891544",
            "extra": "mean: 39.232218499999654 msec\nrounds: 26"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 24.173840788162114,
            "unit": "iter/sec",
            "range": "stddev: 0.00034961256310530486",
            "extra": "mean: 41.36703012000055 msec\nrounds: 25"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 23.326152752455805,
            "unit": "iter/sec",
            "range": "stddev: 0.00022833575852062665",
            "extra": "mean: 42.870335739129494 msec\nrounds: 23"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 89.88139816950292,
            "unit": "iter/sec",
            "range": "stddev: 0.0016019884614915595",
            "extra": "mean: 11.125772633333417 msec\nrounds: 90"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 27.831846938756936,
            "unit": "iter/sec",
            "range": "stddev: 0.0001274324952147562",
            "extra": "mean: 35.930062500001064 msec\nrounds: 28"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 43.960379960235485,
            "unit": "iter/sec",
            "range": "stddev: 0.00012218473971940051",
            "extra": "mean: 22.747756068181246 msec\nrounds: 44"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 72.71735124042482,
            "unit": "iter/sec",
            "range": "stddev: 0.00016685176970284018",
            "extra": "mean: 13.75187603703699 msec\nrounds: 81"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 89.48712854658645,
            "unit": "iter/sec",
            "range": "stddev: 0.0019352652083333456",
            "extra": "mean: 11.174791461538586 msec\nrounds: 91"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 39.89487831217731,
            "unit": "iter/sec",
            "range": "stddev: 0.00023313361664593636",
            "extra": "mean: 25.06587417500068 msec\nrounds: 40"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 31623.691521952966,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020781048623693772",
            "extra": "mean: 31.62186170788462 usec\nrounds: 14708"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 30927.657654203475,
            "unit": "iter/sec",
            "range": "stddev: 0.000002265301045446749",
            "extra": "mean: 32.33351879346371 usec\nrounds: 12797"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 48740.41961706671,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017550098689873773",
            "extra": "mean: 20.51685249853378 usec\nrounds: 13688"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 33300.07158134875,
            "unit": "iter/sec",
            "range": "stddev: 0.000011653556091790256",
            "extra": "mean: 30.029965477914967 usec\nrounds: 11413"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 66311.94329322116,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014878288033210432",
            "extra": "mean: 15.080239702494534 usec\nrounds: 22991"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 62521.380740545355,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015431107659983671",
            "extra": "mean: 15.994528402209392 usec\nrounds: 18238"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 31117.041788291728,
            "unit": "iter/sec",
            "range": "stddev: 0.000010122037304141032",
            "extra": "mean: 32.13673095288465 usec\nrounds: 9634"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 28969.855313003216,
            "unit": "iter/sec",
            "range": "stddev: 0.000008570360819864957",
            "extra": "mean: 34.518639779023914 usec\nrounds: 9955"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 6350.043755751265,
            "unit": "iter/sec",
            "range": "stddev: 0.000032917363343205204",
            "extra": "mean: 157.47922982330556 usec\nrounds: 2602"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1422.7000590113046,
            "unit": "iter/sec",
            "range": "stddev: 0.0008278524030944411",
            "extra": "mean: 702.8888441144389 usec\nrounds: 943"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 7324.647922242696,
            "unit": "iter/sec",
            "range": "stddev: 0.0005212214573775777",
            "extra": "mean: 136.52533345163368 usec\nrounds: 8457"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 74.76713260656437,
            "unit": "iter/sec",
            "range": "stddev: 0.0026315957811042096",
            "extra": "mean: 13.37486092000006 msec\nrounds: 75"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 57.09150653684229,
            "unit": "iter/sec",
            "range": "stddev: 0.00013199307407671206",
            "extra": "mean: 17.515740267857183 msec\nrounds: 56"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 598.4057780460754,
            "unit": "iter/sec",
            "range": "stddev: 0.00004817747932965066",
            "extra": "mean: 1.671106858735918 msec\nrounds: 538"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 185.09266903210857,
            "unit": "iter/sec",
            "range": "stddev: 0.005303205932204281",
            "extra": "mean: 5.402699119469324 msec\nrounds: 226"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 79.10254399369244,
            "unit": "iter/sec",
            "range": "stddev: 0.0002694791322756256",
            "extra": "mean: 12.641818448718148 msec\nrounds: 78"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 560.0738183962715,
            "unit": "iter/sec",
            "range": "stddev: 0.0019063833571625383",
            "extra": "mean: 1.785478926444774 msec\nrounds: 571"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 192.64532768950596,
            "unit": "iter/sec",
            "range": "stddev: 0.005068141702002248",
            "extra": "mean: 5.190886340164654 msec\nrounds: 244"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "committer": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "distinct": true,
          "id": "97051410dac580c862f1d4426e0d6e56c93c7991",
          "message": "docs: add a GitHub Pages documentation site\n\nBuild the existing Markdown docs with MkDocs Material, add getting-started\nand examples landing pages, fix links that escaped docs/, and deploy through\nGitHub Actions Pages.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-20T04:24:19+08:00",
          "tree_id": "de4056657ccdedc90be3a94949b6769a62fefe9f",
          "url": "https://github.com/fyabc/oort-lang.py/commit/97051410dac580c862f1d4426e0d6e56c93c7991"
        },
        "date": 1795119907160,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 20.4639008058516,
            "unit": "iter/sec",
            "range": "stddev: 0.005174830608578617",
            "extra": "mean: 48.866538666667715 msec\nrounds: 6"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.5870539554942147,
            "unit": "iter/sec",
            "range": "stddev: 0.006604200648046094",
            "extra": "mean: 630.0983003999988 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 25.001313458425322,
            "unit": "iter/sec",
            "range": "stddev: 0.0005502069300115505",
            "extra": "mean: 39.997898576924754 msec\nrounds: 26"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 22.53085454814563,
            "unit": "iter/sec",
            "range": "stddev: 0.0003922955623109937",
            "extra": "mean: 44.38358065217298 msec\nrounds: 23"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 20.880038374886073,
            "unit": "iter/sec",
            "range": "stddev: 0.0005221470433414668",
            "extra": "mean: 47.892632285713226 msec\nrounds: 21"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 91.18033504230596,
            "unit": "iter/sec",
            "range": "stddev: 0.0021714290003040397",
            "extra": "mean: 10.967277094737794 msec\nrounds: 95"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 26.683194276733172,
            "unit": "iter/sec",
            "range": "stddev: 0.0005388683967695208",
            "extra": "mean: 37.47677244444326 msec\nrounds: 27"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 42.83150444305142,
            "unit": "iter/sec",
            "range": "stddev: 0.00038487082583340594",
            "extra": "mean: 23.34730038095196 msec\nrounds: 42"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 81.3307053679169,
            "unit": "iter/sec",
            "range": "stddev: 0.00015988505858249464",
            "extra": "mean: 12.295479247060323 msec\nrounds: 85"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 91.97252904091297,
            "unit": "iter/sec",
            "range": "stddev: 0.0021135952608015937",
            "extra": "mean: 10.872811810526173 msec\nrounds: 95"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 38.54392305612894,
            "unit": "iter/sec",
            "range": "stddev: 0.0004391071863142833",
            "extra": "mean: 25.944427051282943 msec\nrounds: 39"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 32792.170849865564,
            "unit": "iter/sec",
            "range": "stddev: 0.000002509227926225645",
            "extra": "mean: 30.495083859448105 usec\nrounds: 15526"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 31234.772159398075,
            "unit": "iter/sec",
            "range": "stddev: 0.0000030473585416213517",
            "extra": "mean: 32.0156009109583 usec\nrounds: 13829"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 43514.92906716039,
            "unit": "iter/sec",
            "range": "stddev: 0.0000024361885430296094",
            "extra": "mean: 22.980618868908476 usec\nrounds: 12783"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 28985.401926898165,
            "unit": "iter/sec",
            "range": "stddev: 0.000008665624657437881",
            "extra": "mean: 34.50012535696494 usec\nrounds: 10155"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 66136.25426361863,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017329416531129577",
            "extra": "mean: 15.120299919224445 usec\nrounds: 19822"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 60295.42899340054,
            "unit": "iter/sec",
            "range": "stddev: 0.0000024057211981316032",
            "extra": "mean: 16.585005143747335 usec\nrounds: 16525"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 27155.341415331488,
            "unit": "iter/sec",
            "range": "stddev: 0.0000073559245889520074",
            "extra": "mean: 36.82516764217206 usec\nrounds: 10081"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 25470.091738512172,
            "unit": "iter/sec",
            "range": "stddev: 0.000007481630824435489",
            "extra": "mean: 39.261735303761995 usec\nrounds: 9101"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 5808.261706481138,
            "unit": "iter/sec",
            "range": "stddev: 0.00003023155857279577",
            "extra": "mean: 172.168550684304 usec\nrounds: 2851"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1450.2402969426116,
            "unit": "iter/sec",
            "range": "stddev: 0.000792437611094812",
            "extra": "mean: 689.5409002964504 usec\nrounds: 1013"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 8263.557086491232,
            "unit": "iter/sec",
            "range": "stddev: 0.0004397163903672762",
            "extra": "mean: 121.01326215011453 usec\nrounds: 10185"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 75.28031842027306,
            "unit": "iter/sec",
            "range": "stddev: 0.003181384159876803",
            "extra": "mean: 13.283684513888813 msec\nrounds: 72"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 56.421170326134245,
            "unit": "iter/sec",
            "range": "stddev: 0.0005941393744298112",
            "extra": "mean: 17.723843625001884 msec\nrounds: 56"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 596.5224331384421,
            "unit": "iter/sec",
            "range": "stddev: 0.00009684349888854755",
            "extra": "mean: 1.6763828893052175 msec\nrounds: 533"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 237.66405567787473,
            "unit": "iter/sec",
            "range": "stddev: 0.004620997922083601",
            "extra": "mean: 4.20761985714567 msec\nrounds: 35"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 78.53857652600182,
            "unit": "iter/sec",
            "range": "stddev: 0.0027578500414994185",
            "extra": "mean: 12.732596441557982 msec\nrounds: 77"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 735.9131290116624,
            "unit": "iter/sec",
            "range": "stddev: 0.001781679918564888",
            "extra": "mean: 1.3588560396293088 msec\nrounds: 757"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 233.01585599359723,
            "unit": "iter/sec",
            "range": "stddev: 0.004793142569146947",
            "extra": "mean: 4.2915534470215535 msec\nrounds: 302"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "committer": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "distinct": true,
          "id": "56c7a2a8f92d6261acbc975653f1dc476b6c01cf",
          "message": "docs: use the Oort logo on the site and propose minimal IO\n\nReplace the default Material book icon with the Oort orbit/comet icon, and\nadd OP 0015 for file I/O, process arguments, exit codes and string ord/chr.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-20T04:29:28+08:00",
          "tree_id": "a260ab3ca8157d905fdb96c3ac0820cdf44500eb",
          "url": "https://github.com/fyabc/oort-lang.py/commit/56c7a2a8f92d6261acbc975653f1dc476b6c01cf"
        },
        "date": 1795120211556,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 21.815732041804672,
            "unit": "iter/sec",
            "range": "stddev: 0.004176429074060969",
            "extra": "mean: 45.83848014285 msec\nrounds: 7"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.1071558718405607,
            "unit": "iter/sec",
            "range": "stddev: 0.0022974169038890947",
            "extra": "mean: 474.5733400000063 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 32.82192564252913,
            "unit": "iter/sec",
            "range": "stddev: 0.00012876033674160824",
            "extra": "mean: 30.467438470588892 msec\nrounds: 34"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 30.778388218013536,
            "unit": "iter/sec",
            "range": "stddev: 0.00013512836776625152",
            "extra": "mean: 32.490330322584406 msec\nrounds: 31"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 29.878765385626043,
            "unit": "iter/sec",
            "range": "stddev: 0.00016319746364793804",
            "extra": "mean: 33.46858503333863 msec\nrounds: 30"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 115.49566013260888,
            "unit": "iter/sec",
            "range": "stddev: 0.0012709730358307241",
            "extra": "mean: 8.65833399152685 msec\nrounds: 118"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 35.91628903903856,
            "unit": "iter/sec",
            "range": "stddev: 0.00024058477466318916",
            "extra": "mean: 27.842520114287645 msec\nrounds: 35"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 56.51989674416386,
            "unit": "iter/sec",
            "range": "stddev: 0.00013983236745834053",
            "extra": "mean: 17.692884410714324 msec\nrounds: 56"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 92.92210092817922,
            "unit": "iter/sec",
            "range": "stddev: 0.00016274235096852923",
            "extra": "mean: 10.761702436892962 msec\nrounds: 103"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 116.85434409831119,
            "unit": "iter/sec",
            "range": "stddev: 0.001559459223955988",
            "extra": "mean: 8.557662170938942 msec\nrounds: 117"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 50.76391373852791,
            "unit": "iter/sec",
            "range": "stddev: 0.0002762559206530516",
            "extra": "mean: 19.699032764706583 msec\nrounds: 51"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 40576.51465330253,
            "unit": "iter/sec",
            "range": "stddev: 0.0000024433983841648464",
            "extra": "mean: 24.644797823181438 usec\nrounds: 20764"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 39090.695152677654,
            "unit": "iter/sec",
            "range": "stddev: 0.000001920625057496231",
            "extra": "mean: 25.581535352448224 usec\nrounds: 17269"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 61959.352222058675,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013537429287201287",
            "extra": "mean: 16.139613539148357 usec\nrounds: 17549"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 42787.34155670168,
            "unit": "iter/sec",
            "range": "stddev: 0.000008263822251642457",
            "extra": "mean: 23.371398259805474 usec\nrounds: 14596"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 83534.65503265624,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010868960943052164",
            "extra": "mean: 11.971079543083878 usec\nrounds: 23899"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 76928.7740475724,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012488880680995617",
            "extra": "mean: 12.999037257263513 usec\nrounds: 20855"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 39926.53752648493,
            "unit": "iter/sec",
            "range": "stddev: 0.000008776877162034231",
            "extra": "mean: 25.045998525082684 usec\nrounds: 10848"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 33585.939736078995,
            "unit": "iter/sec",
            "range": "stddev: 0.00026898388793208315",
            "extra": "mean: 29.774364149345832 usec\nrounds: 10633"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 7741.082688080639,
            "unit": "iter/sec",
            "range": "stddev: 0.000037739948135061727",
            "extra": "mean: 129.18089630275537 usec\nrounds: 2488"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1921.8414903942687,
            "unit": "iter/sec",
            "range": "stddev: 0.00012071304466198525",
            "extra": "mean: 520.3342757444832 usec\nrounds: 1175"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 9391.402794923057,
            "unit": "iter/sec",
            "range": "stddev: 0.00037089623901764065",
            "extra": "mean: 106.48036526988224 usec\nrounds: 11575"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 95.81949496942754,
            "unit": "iter/sec",
            "range": "stddev: 0.0024515274961883406",
            "extra": "mean: 10.436289612245014 msec\nrounds: 98"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 73.19061131826894,
            "unit": "iter/sec",
            "range": "stddev: 0.0003203073932671238",
            "extra": "mean: 13.662954605632489 msec\nrounds: 71"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 767.7143740215123,
            "unit": "iter/sec",
            "range": "stddev: 0.00005356859611703319",
            "extra": "mean: 1.302567769783582 msec\nrounds: 695"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 247.930518794491,
            "unit": "iter/sec",
            "range": "stddev: 0.0042179003147762495",
            "extra": "mean: 4.033388083331918 msec\nrounds: 36"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 101.24180033551248,
            "unit": "iter/sec",
            "range": "stddev: 0.00236539972812489",
            "extra": "mean: 9.87734311999617 msec\nrounds: 100"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 736.1981342428049,
            "unit": "iter/sec",
            "range": "stddev: 0.001635696051212358",
            "extra": "mean: 1.3583299841265162 msec\nrounds: 756"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 245.69679461394384,
            "unit": "iter/sec",
            "range": "stddev: 0.004543683186056319",
            "extra": "mean: 4.070057167702455 msec\nrounds: 322"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "committer": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "distinct": true,
          "id": "c505572346d4bd87971ba61655e0bf5d48471807",
          "message": "feat: add minimal IO, process args, and a JSON CLI example\n\nImplement OP 0015: io.read_file/write_file, os.args/script/exit, and\nstring.ord/chr. Add a recursive-descent JSON parser/formatter showcase with\nUnicode escapes, surrogate pairs, file input and error exit codes.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-20T04:48:12+08:00",
          "tree_id": "6039225a43118e40c51d89d382d56c286130c0c7",
          "url": "https://github.com/fyabc/oort-lang.py/commit/c505572346d4bd87971ba61655e0bf5d48471807"
        },
        "date": 1795121334874,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 24.016228712669307,
            "unit": "iter/sec",
            "range": "stddev: 0.00683188708086607",
            "extra": "mean: 41.6385108571384 msec\nrounds: 7"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.888094643351301,
            "unit": "iter/sec",
            "range": "stddev: 0.0022516726655031336",
            "extra": "mean: 346.24904079999794 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 46.398541210068935,
            "unit": "iter/sec",
            "range": "stddev: 0.000209648740886379",
            "extra": "mean: 21.552401733332733 msec\nrounds: 45"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 43.64258702599054,
            "unit": "iter/sec",
            "range": "stddev: 0.00027104547743779343",
            "extra": "mean: 22.913398772727852 msec\nrounds: 44"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 41.21225871370195,
            "unit": "iter/sec",
            "range": "stddev: 0.00032516152836737456",
            "extra": "mean: 24.264624924999012 msec\nrounds: 40"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 161.60877346207693,
            "unit": "iter/sec",
            "range": "stddev: 0.0024699011082451347",
            "extra": "mean: 6.187782869564688 msec\nrounds: 161"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 49.6827486790475,
            "unit": "iter/sec",
            "range": "stddev: 0.0005691879836284531",
            "extra": "mean: 20.127710857143576 msec\nrounds: 49"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 80.00683544714417,
            "unit": "iter/sec",
            "range": "stddev: 0.00025302501805990203",
            "extra": "mean: 12.498932052632446 msec\nrounds: 76"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 104.62702202383828,
            "unit": "iter/sec",
            "range": "stddev: 0.0005553912544677954",
            "extra": "mean: 9.557760324786456 msec\nrounds: 117"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 159.62917031617403,
            "unit": "iter/sec",
            "range": "stddev: 0.002664889362994061",
            "extra": "mean: 6.264519185430343 msec\nrounds: 151"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 71.23512981676228,
            "unit": "iter/sec",
            "range": "stddev: 0.00028695105928765624",
            "extra": "mean: 14.038017514283954 msec\nrounds: 70"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 57744.79345964931,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019691359542017536",
            "extra": "mean: 17.31757860903557 usec\nrounds: 13529"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 55827.942427655245,
            "unit": "iter/sec",
            "range": "stddev: 0.000001333882967715564",
            "extra": "mean: 17.912177245218235 usec\nrounds: 13896"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 89316.70889210877,
            "unit": "iter/sec",
            "range": "stddev: 9.844347537669892e-7",
            "extra": "mean: 11.196113385771552 usec\nrounds: 13873"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 50832.17140563121,
            "unit": "iter/sec",
            "range": "stddev: 0.000013692941713880702",
            "extra": "mean: 19.67258081540895 usec\nrounds: 11749"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 118403.28942996985,
            "unit": "iter/sec",
            "range": "stddev: 8.128589269755208e-7",
            "extra": "mean: 8.445711304257763 usec\nrounds: 19789"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 111947.44453371334,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013818405204365981",
            "extra": "mean: 8.93276308508183 usec\nrounds: 17711"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 55090.14297605821,
            "unit": "iter/sec",
            "range": "stddev: 0.000005807507479126463",
            "extra": "mean: 18.152067610980662 usec\nrounds: 9954"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 48235.13735629307,
            "unit": "iter/sec",
            "range": "stddev: 0.000005685306041202544",
            "extra": "mean: 20.73177469390027 usec\nrounds: 11025"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 8523.756099820179,
            "unit": "iter/sec",
            "range": "stddev: 0.000024294241050007366",
            "extra": "mean: 117.31917106603936 usec\nrounds: 2993"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 2417.2759313238703,
            "unit": "iter/sec",
            "range": "stddev: 0.00013795176199179443",
            "extra": "mean: 413.6888085640805 usec\nrounds: 1191"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 11764.91908293863,
            "unit": "iter/sec",
            "range": "stddev: 0.0006975851680807267",
            "extra": "mean: 84.99845965368263 usec\nrounds: 13917"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 131.90620202734772,
            "unit": "iter/sec",
            "range": "stddev: 0.0038097169322201824",
            "extra": "mean: 7.581144666667553 msec\nrounds: 132"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 97.48561475947378,
            "unit": "iter/sec",
            "range": "stddev: 0.0046247409619740885",
            "extra": "mean: 10.257923720000122 msec\nrounds: 100"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 1079.969332921133,
            "unit": "iter/sec",
            "range": "stddev: 0.000040008209251243815",
            "extra": "mean: 925.9522187497403 usec\nrounds: 896"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 231.238148828089,
            "unit": "iter/sec",
            "range": "stddev: 0.010096384410887227",
            "extra": "mean: 4.324545949999958 msec\nrounds: 20"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 133.17684726678155,
            "unit": "iter/sec",
            "range": "stddev: 0.004929749840671443",
            "extra": "mean: 7.508812684210697 msec\nrounds: 95"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 894.4866319071024,
            "unit": "iter/sec",
            "range": "stddev: 0.0032290059910100033",
            "extra": "mean: 1.1179596925534105 msec\nrounds: 940"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 220.33667509125158,
            "unit": "iter/sec",
            "range": "stddev: 0.010334719944741314",
            "extra": "mean: 4.538509077464539 msec\nrounds: 426"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "committer": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "distinct": true,
          "id": "4ba25572edbc43dcfb22843d56b0051da45ec570",
          "message": "docs: add Oort welcome page; test: speed up and add slow marker\n\nAdd the Oort-cloud welcome text to the docs homepage. Compile the JSON\nshowcase once per test module, move it out of the generic example matrix, and\nmark it slow. The default suite now skips slow tests and CI runs them in a\nparallel job.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-20T05:00:36+08:00",
          "tree_id": "88b1091ccfd2a11e857696be648c951a16001f4c",
          "url": "https://github.com/fyabc/oort-lang.py/commit/4ba25572edbc43dcfb22843d56b0051da45ec570"
        },
        "date": 1795122081765,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 21.519363930636153,
            "unit": "iter/sec",
            "range": "stddev: 0.006023764950203041",
            "extra": "mean: 46.46977500001034 msec\nrounds: 6"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.6005975642776054,
            "unit": "iter/sec",
            "range": "stddev: 0.013868484284468614",
            "extra": "mean: 624.7666635999963 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 24.84270565162762,
            "unit": "iter/sec",
            "range": "stddev: 0.0003373013333073301",
            "extra": "mean: 40.25326443999802 msec\nrounds: 25"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 21.921853874104983,
            "unit": "iter/sec",
            "range": "stddev: 0.00047164037157241656",
            "extra": "mean: 45.61657995454673 msec\nrounds: 22"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 20.335110930603218,
            "unit": "iter/sec",
            "range": "stddev: 0.0010218163160154536",
            "extra": "mean: 49.17602876191127 msec\nrounds: 21"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 91.45439665702906,
            "unit": "iter/sec",
            "range": "stddev: 0.0017540803564199089",
            "extra": "mean: 10.934411428574453 msec\nrounds: 91"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 25.9150418114075,
            "unit": "iter/sec",
            "range": "stddev: 0.000455197220230073",
            "extra": "mean: 38.58762826922438 msec\nrounds: 26"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 41.714157556777494,
            "unit": "iter/sec",
            "range": "stddev: 0.0003887213756783996",
            "extra": "mean: 23.972676390237332 msec\nrounds: 41"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 90.10991375841189,
            "unit": "iter/sec",
            "range": "stddev: 0.00014681618897740203",
            "extra": "mean: 11.097558063156493 msec\nrounds: 95"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 91.08984684087268,
            "unit": "iter/sec",
            "range": "stddev: 0.002185723622109421",
            "extra": "mean: 10.978171933332229 msec\nrounds: 90"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 38.48403834151185,
            "unit": "iter/sec",
            "range": "stddev: 0.0004837012120638894",
            "extra": "mean: 25.984798973690946 msec\nrounds: 38"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 30808.750588966457,
            "unit": "iter/sec",
            "range": "stddev: 0.000002999325041954794",
            "extra": "mean: 32.458310735850816 usec\nrounds: 13143"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 30807.343620960775,
            "unit": "iter/sec",
            "range": "stddev: 0.000003243773776071069",
            "extra": "mean: 32.45979310334363 usec\nrounds: 14123"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 41572.627985042105,
            "unit": "iter/sec",
            "range": "stddev: 0.0000028376372600530283",
            "extra": "mean: 24.054288806562855 usec\nrounds: 12981"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 28005.719635263245,
            "unit": "iter/sec",
            "range": "stddev: 0.000008781677837332273",
            "extra": "mean: 35.706991751101285 usec\nrounds: 10426"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 63844.32436582069,
            "unit": "iter/sec",
            "range": "stddev: 0.000001991410581430231",
            "extra": "mean: 15.663099420868079 usec\nrounds: 19503"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 60016.93408941647,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021236593744141427",
            "extra": "mean: 16.661964080173536 usec\nrounds: 17205"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 26240.436113852975,
            "unit": "iter/sec",
            "range": "stddev: 0.000009888086985404442",
            "extra": "mean: 38.10912271660284 usec\nrounds: 10292"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 24278.310931397347,
            "unit": "iter/sec",
            "range": "stddev: 0.000009377813444256681",
            "extra": "mean: 41.189026815978934 usec\nrounds: 9994"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 5171.957440708919,
            "unit": "iter/sec",
            "range": "stddev: 0.000033602417022087626",
            "extra": "mean: 193.35039227680306 usec\nrounds: 2771"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1393.2199110054853,
            "unit": "iter/sec",
            "range": "stddev: 0.0007680008458540344",
            "extra": "mean: 717.761777663873 usec\nrounds: 976"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 8129.051493278927,
            "unit": "iter/sec",
            "range": "stddev: 0.0005257327074033423",
            "extra": "mean: 123.01558193188917 usec\nrounds: 3509"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 75.13071821488856,
            "unit": "iter/sec",
            "range": "stddev: 0.00016136201413384136",
            "extra": "mean: 13.310134972220075 msec\nrounds: 72"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 55.134999424470806,
            "unit": "iter/sec",
            "range": "stddev: 0.0012841042558338449",
            "extra": "mean: 18.137299545452898 msec\nrounds: 55"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 580.6125275888609,
            "unit": "iter/sec",
            "range": "stddev: 0.000051969415264330155",
            "extra": "mean: 1.722319020832621 msec\nrounds: 528"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 212.93979259696926,
            "unit": "iter/sec",
            "range": "stddev: 0.005507857071538026",
            "extra": "mean: 4.696163116363591 msec\nrounds: 275"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 75.90026631668857,
            "unit": "iter/sec",
            "range": "stddev: 0.0027418032321529294",
            "extra": "mean: 13.175184337661868 msec\nrounds: 77"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 711.3681115397734,
            "unit": "iter/sec",
            "range": "stddev: 0.0018056489428529751",
            "extra": "mean: 1.4057419552241046 msec\nrounds: 737"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 224.34422505978978,
            "unit": "iter/sec",
            "range": "stddev: 0.005355741917754979",
            "extra": "mean: 4.457435887790252 msec\nrounds: 303"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "committer": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "distinct": true,
          "id": "2600bad3ec3ea9ae2c57953ecd0abed477adfd07",
          "message": "release: 0.3.0\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-20T05:08:33+08:00",
          "tree_id": "a1d15ab61440575fd0f6e7417eac80558556eaae",
          "url": "https://github.com/fyabc/oort-lang.py/commit/2600bad3ec3ea9ae2c57953ecd0abed477adfd07"
        },
        "date": 1795122562801,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 37.51069697234313,
            "unit": "iter/sec",
            "range": "stddev: 0.003512823466300935",
            "extra": "mean: 26.659062100000597 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.1014972756616097,
            "unit": "iter/sec",
            "range": "stddev: 0.0015960561246774216",
            "extra": "mean: 475.85119979999604 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 31.757632260901836,
            "unit": "iter/sec",
            "range": "stddev: 0.00028671303534352896",
            "extra": "mean: 31.488493593747613 msec\nrounds: 32"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 28.272042584254383,
            "unit": "iter/sec",
            "range": "stddev: 0.0009910034020309613",
            "extra": "mean: 35.37063150000108 msec\nrounds: 30"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 26.05416337493984,
            "unit": "iter/sec",
            "range": "stddev: 0.0006650910268968484",
            "extra": "mean: 38.38158169230829 msec\nrounds: 26"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 116.51297382750852,
            "unit": "iter/sec",
            "range": "stddev: 0.00011364454969469633",
            "extra": "mean: 8.58273518518589 msec\nrounds: 108"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 33.626203056535545,
            "unit": "iter/sec",
            "range": "stddev: 0.00031254290920032437",
            "extra": "mean: 29.738712941175837 msec\nrounds: 34"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 53.80912386752752,
            "unit": "iter/sec",
            "range": "stddev: 0.00020507041154736966",
            "extra": "mean: 18.584208924529165 msec\nrounds: 53"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 160.84503154221485,
            "unit": "iter/sec",
            "range": "stddev: 0.00015866338170094038",
            "extra": "mean: 6.217164374999941 msec\nrounds: 168"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 115.36392519553748,
            "unit": "iter/sec",
            "range": "stddev: 0.0015865579211761",
            "extra": "mean: 8.668221008474166 msec\nrounds: 118"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 49.183888476316,
            "unit": "iter/sec",
            "range": "stddev: 0.0002880374582361456",
            "extra": "mean: 20.331861326530536 msec\nrounds: 49"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 41203.64876752429,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020234262059890626",
            "extra": "mean: 24.269695279709683 usec\nrounds: 17393"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 39048.67682074195,
            "unit": "iter/sec",
            "range": "stddev: 0.000002028817829323982",
            "extra": "mean: 25.609062365688615 usec\nrounds: 17221"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 57236.560540849576,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018111866328100643",
            "extra": "mean: 17.471350314390445 usec\nrounds: 17176"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 36242.19960102415,
            "unit": "iter/sec",
            "range": "stddev: 0.000008869694074840068",
            "extra": "mean: 27.592144268521203 usec\nrounds: 12449"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 81627.53138496929,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013771302751386783",
            "extra": "mean: 12.25076861976666 usec\nrounds: 27068"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 75961.93108002485,
            "unit": "iter/sec",
            "range": "stddev: 0.00000134070209791726",
            "extra": "mean: 13.164488919410353 usec\nrounds: 21840"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 33978.80126026539,
            "unit": "iter/sec",
            "range": "stddev: 0.000005672592053334121",
            "extra": "mean: 29.430114156775566 usec\nrounds: 11747"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 29349.758160800222,
            "unit": "iter/sec",
            "range": "stddev: 0.00018496590505535113",
            "extra": "mean: 34.0718310018516 usec\nrounds: 12367"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 6725.698619978645,
            "unit": "iter/sec",
            "range": "stddev: 0.000025269316424443913",
            "extra": "mean: 148.68343892625614 usec\nrounds: 2980"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1905.180128682745,
            "unit": "iter/sec",
            "range": "stddev: 0.00012468590588208758",
            "extra": "mean: 524.8847523364666 usec\nrounds: 1284"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 10515.714440814514,
            "unit": "iter/sec",
            "range": "stddev: 0.00035360035114345744",
            "extra": "mean: 95.09577362796314 usec\nrounds: 11808"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 94.39779511870388,
            "unit": "iter/sec",
            "range": "stddev: 0.002127850302842704",
            "extra": "mean: 10.593467768421013 msec\nrounds: 95"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 71.59689665597975,
            "unit": "iter/sec",
            "range": "stddev: 0.00009711281518784518",
            "extra": "mean: 13.967085819444947 msec\nrounds: 72"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 760.4885965470409,
            "unit": "iter/sec",
            "range": "stddev: 0.000031615351585939664",
            "extra": "mean: 1.3149441090115594 msec\nrounds: 688"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 281.84882717957265,
            "unit": "iter/sec",
            "range": "stddev: 0.003954924062492792",
            "extra": "mean: 3.5480012814205395 msec\nrounds: 366"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 96.59553065405224,
            "unit": "iter/sec",
            "range": "stddev: 0.00228045394452615",
            "extra": "mean: 10.352445845361164 msec\nrounds: 97"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 944.0165125958339,
            "unit": "iter/sec",
            "range": "stddev: 0.0014540406016580445",
            "extra": "mean: 1.0593035043955152 msec\nrounds: 910"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 304.81793499231895,
            "unit": "iter/sec",
            "range": "stddev: 0.003407757233282239",
            "extra": "mean: 3.280646855721265 msec\nrounds: 402"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "committer": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "distinct": true,
          "id": "46886b3ead29c8d3a8161a3193d5def3ec52aae1",
          "message": "docs: propose a unified equality protocol\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-20T05:21:12+08:00",
          "tree_id": "bcc16d09f6cedb424afa253a5d7f4eb6a61d3971",
          "url": "https://github.com/fyabc/oort-lang.py/commit/46886b3ead29c8d3a8161a3193d5def3ec52aae1"
        },
        "date": 1795123315271,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 21.456568111905682,
            "unit": "iter/sec",
            "range": "stddev: 0.0052070541093384715",
            "extra": "mean: 46.605775666665274 msec\nrounds: 6"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.0999387988796503,
            "unit": "iter/sec",
            "range": "stddev: 0.004716325982259366",
            "extra": "mean: 476.2043544000022 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 32.374882268984365,
            "unit": "iter/sec",
            "range": "stddev: 0.0004933981126367728",
            "extra": "mean: 30.888143212122674 msec\nrounds: 33"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 30.41087726212537,
            "unit": "iter/sec",
            "range": "stddev: 0.00014532190558146896",
            "extra": "mean: 32.88297116129006 msec\nrounds: 31"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 29.115981699171474,
            "unit": "iter/sec",
            "range": "stddev: 0.00026588812449677",
            "extra": "mean: 34.345398700001795 msec\nrounds: 30"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 113.16216681683846,
            "unit": "iter/sec",
            "range": "stddev: 0.0013470941557751268",
            "extra": "mean: 8.836875681415465 msec\nrounds: 113"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 35.4051647025062,
            "unit": "iter/sec",
            "range": "stddev: 0.00024009983029859544",
            "extra": "mean: 28.244466828570175 msec\nrounds: 35"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 55.11134492215625,
            "unit": "iter/sec",
            "range": "stddev: 0.00022002849420445117",
            "extra": "mean: 18.14508430909246 msec\nrounds: 55"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 92.2028911730103,
            "unit": "iter/sec",
            "range": "stddev: 0.00020083651092497523",
            "extra": "mean: 10.845646891089254 msec\nrounds: 101"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 111.19852907225969,
            "unit": "iter/sec",
            "range": "stddev: 0.0021699541781550996",
            "extra": "mean: 8.992924711712455 msec\nrounds: 111"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 50.92433651895195,
            "unit": "iter/sec",
            "range": "stddev: 0.00017830819647166003",
            "extra": "mean: 19.636976509803738 msec\nrounds: 51"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 40040.30673779957,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015389126486223608",
            "extra": "mean: 24.974833648213842 usec\nrounds: 17998"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 38627.4353538739,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015255841692883634",
            "extra": "mean: 25.888335346077053 usec\nrounds: 15071"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 61068.17014654897,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012904431982209119",
            "extra": "mean: 16.375142690541406 usec\nrounds: 12860"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 41638.15352925219,
            "unit": "iter/sec",
            "range": "stddev: 0.000009339352407588757",
            "extra": "mean: 24.016434813745207 usec\nrounds: 13960"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 79989.26448716773,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011861421409199347",
            "extra": "mean: 12.501677649010324 usec\nrounds: 23462"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 76298.77235158996,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011024616479112755",
            "extra": "mean: 13.106370773463192 usec\nrounds: 22329"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 40045.18122612936,
            "unit": "iter/sec",
            "range": "stddev: 0.000005828657087098628",
            "extra": "mean: 24.971793593669716 usec\nrounds: 11395"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 36129.407968427484,
            "unit": "iter/sec",
            "range": "stddev: 0.000006704425914507651",
            "extra": "mean: 27.67828359860956 usec\nrounds: 11749"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 6912.484654397536,
            "unit": "iter/sec",
            "range": "stddev: 0.0004608560919988009",
            "extra": "mean: 144.6657822761063 usec\nrounds: 3137"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1844.630356364209,
            "unit": "iter/sec",
            "range": "stddev: 0.00012727517687580506",
            "extra": "mean: 542.1140319792921 usec\nrounds: 1157"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 9627.603612514406,
            "unit": "iter/sec",
            "range": "stddev: 0.0004029782079807546",
            "extra": "mean: 103.86800706046452 usec\nrounds: 11614"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 94.83377388922356,
            "unit": "iter/sec",
            "range": "stddev: 0.004535927536866357",
            "extra": "mean: 10.544766479167134 msec\nrounds: 96"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 73.17922763716591,
            "unit": "iter/sec",
            "range": "stddev: 0.00006892689048355202",
            "extra": "mean: 13.665079999998865 msec\nrounds: 73"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 767.0609856487324,
            "unit": "iter/sec",
            "range": "stddev: 0.0000386338983416812",
            "extra": "mean: 1.3036773069018266 msec\nrounds: 681"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 215.52887057503358,
            "unit": "iter/sec",
            "range": "stddev: 0.005879156487402138",
            "extra": "mean: 4.639749641576965 msec\nrounds: 279"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 102.56024464135496,
            "unit": "iter/sec",
            "range": "stddev: 0.00015769670016588193",
            "extra": "mean: 9.750366757576687 msec\nrounds: 99"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 732.328551638723,
            "unit": "iter/sec",
            "range": "stddev: 0.0017683424390934378",
            "extra": "mean: 1.3655073228570862 msec\nrounds: 700"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 239.81650470739768,
            "unit": "iter/sec",
            "range": "stddev: 0.005113424891186134",
            "extra": "mean: 4.169854786350545 msec\nrounds: 337"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "committer": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "distinct": true,
          "id": "559dd42289ef8f95ea8a84c86e0804d6abeedcd5",
          "message": "docs: add OP 0016 and equality implementation to site nav\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-20T05:30:14+08:00",
          "tree_id": "6168ba70bd20c2933514326a80f4c09e70026c24",
          "url": "https://github.com/fyabc/oort-lang.py/commit/559dd42289ef8f95ea8a84c86e0804d6abeedcd5"
        },
        "date": 1795123855303,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 25.114373761963364,
            "unit": "iter/sec",
            "range": "stddev: 0.0051164773658932015",
            "extra": "mean: 39.817835374996946 msec\nrounds: 8"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.889071605333563,
            "unit": "iter/sec",
            "range": "stddev: 0.0029489930207537234",
            "extra": "mean: 346.131953999992 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 46.82284035208275,
            "unit": "iter/sec",
            "range": "stddev: 0.0002602897230770101",
            "extra": "mean: 21.35709821276399 msec\nrounds: 47"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 43.57857626794751,
            "unit": "iter/sec",
            "range": "stddev: 0.00043873529676049855",
            "extra": "mean: 22.947055311109605 msec\nrounds: 45"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 41.25280685355488,
            "unit": "iter/sec",
            "range": "stddev: 0.0017452408696305426",
            "extra": "mean: 24.240774780488103 msec\nrounds: 41"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 165.07040001368173,
            "unit": "iter/sec",
            "range": "stddev: 0.00013722431595421903",
            "extra": "mean: 6.05802130434721 msec\nrounds: 161"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 50.25746350749174,
            "unit": "iter/sec",
            "range": "stddev: 0.0003107201292959223",
            "extra": "mean: 19.89754217999746 msec\nrounds: 50"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 80.40342380787513,
            "unit": "iter/sec",
            "range": "stddev: 0.00029384805854820164",
            "extra": "mean: 12.437281307690467 msec\nrounds: 78"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 104.40821972206841,
            "unit": "iter/sec",
            "range": "stddev: 0.00021133432905080042",
            "extra": "mean: 9.577789973451997 msec\nrounds: 113"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 158.78305286308674,
            "unit": "iter/sec",
            "range": "stddev: 0.003012015673704273",
            "extra": "mean: 6.2979013312098635 msec\nrounds: 157"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 70.6910255414302,
            "unit": "iter/sec",
            "range": "stddev: 0.00026901277281852175",
            "extra": "mean: 14.146067231885407 msec\nrounds: 69"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 58200.163848847405,
            "unit": "iter/sec",
            "range": "stddev: 0.0000034481465611808634",
            "extra": "mean: 17.182082211952466 usec\nrounds: 18951"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 56138.02380974657,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011975418833438992",
            "extra": "mean: 17.813238374564623 usec\nrounds: 16709"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 90087.27779233332,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010102462715729324",
            "extra": "mean: 11.100346514023567 usec\nrounds: 15705"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 56226.920327369095,
            "unit": "iter/sec",
            "range": "stddev: 0.000006021031964338672",
            "extra": "mean: 17.78507508819114 usec\nrounds: 14463"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 117823.50653537177,
            "unit": "iter/sec",
            "range": "stddev: 0.000001038921935705059",
            "extra": "mean: 8.487270744227853 usec\nrounds: 25260"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 112371.77134870655,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011621635288587028",
            "extra": "mean: 8.899032096742957 usec\nrounds: 20999"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 52933.72551878345,
            "unit": "iter/sec",
            "range": "stddev: 0.0000051749655393025416",
            "extra": "mean: 18.891547689103263 usec\nrounds: 9845"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 42099.614626487,
            "unit": "iter/sec",
            "range": "stddev: 0.0002598681710332924",
            "extra": "mean: 23.75318655223151 usec\nrounds: 11407"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 8619.900396645917,
            "unit": "iter/sec",
            "range": "stddev: 0.000020669835024898936",
            "extra": "mean: 116.010621235149 usec\nrounds: 3287"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 2466.8879265305595,
            "unit": "iter/sec",
            "range": "stddev: 0.00010430837431738536",
            "extra": "mean: 405.3690438245421 usec\nrounds: 1255"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 11494.343745718288,
            "unit": "iter/sec",
            "range": "stddev: 0.0005567570781831742",
            "extra": "mean: 86.99931219409599 usec\nrounds: 5109"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 134.64445122169553,
            "unit": "iter/sec",
            "range": "stddev: 0.0030280809317597135",
            "extra": "mean: 7.426967772726663 msec\nrounds: 132"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 98.5668072779312,
            "unit": "iter/sec",
            "range": "stddev: 0.0035557286749795147",
            "extra": "mean: 10.1454031800003 msec\nrounds: 100"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 1083.3558669957933,
            "unit": "iter/sec",
            "range": "stddev: 0.000030494196293866052",
            "extra": "mean: 923.0577231958472 usec\nrounds: 914"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 342.63966832964667,
            "unit": "iter/sec",
            "range": "stddev: 0.004856673932494692",
            "extra": "mean: 2.9185178846190114 msec\nrounds: 26"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 142.30301507398994,
            "unit": "iter/sec",
            "range": "stddev: 0.0024340920566420644",
            "extra": "mean: 7.027257992250224 msec\nrounds: 129"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 1100.903827856939,
            "unit": "iter/sec",
            "range": "stddev: 0.001974872779817518",
            "extra": "mean: 908.3445571686656 usec\nrounds: 1102"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 297.64718008591143,
            "unit": "iter/sec",
            "range": "stddev: 0.0062250935757819075",
            "extra": "mean: 3.3596824257208313 msec\nrounds: 451"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "committer": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "distinct": true,
          "id": "95e051fc9482d03bfd12bef0797654d2e45ec36b",
          "message": "release: 0.3.1\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-20T05:35:36+08:00",
          "tree_id": "ba7853ee63f87eb3c805e5a5c18cfe90bbe977ea",
          "url": "https://github.com/fyabc/oort-lang.py/commit/95e051fc9482d03bfd12bef0797654d2e45ec36b"
        },
        "date": 1795124178911,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 24.5318927715254,
            "unit": "iter/sec",
            "range": "stddev: 0.005620548742567172",
            "extra": "mean: 40.763263125001004 msec\nrounds: 8"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.8953378546608888,
            "unit": "iter/sec",
            "range": "stddev: 0.0014952794649210378",
            "extra": "mean: 345.3828361999996 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 46.84362987380854,
            "unit": "iter/sec",
            "range": "stddev: 0.0002451971386603712",
            "extra": "mean: 21.34761978723441 msec\nrounds: 47"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 43.423202838827955,
            "unit": "iter/sec",
            "range": "stddev: 0.0001459217313431774",
            "extra": "mean: 23.029162627907876 msec\nrounds: 43"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 40.9034579814343,
            "unit": "iter/sec",
            "range": "stddev: 0.0004045483629460591",
            "extra": "mean: 24.44781075609526 msec\nrounds: 41"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 164.06883693022465,
            "unit": "iter/sec",
            "range": "stddev: 0.00009182617560284289",
            "extra": "mean: 6.095002675159335 msec\nrounds: 157"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 47.49667693134622,
            "unit": "iter/sec",
            "range": "stddev: 0.002398198468012176",
            "extra": "mean: 21.05410451020487 msec\nrounds: 49"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 79.59248646927277,
            "unit": "iter/sec",
            "range": "stddev: 0.00047064538189476576",
            "extra": "mean: 12.564000000000716 msec\nrounds: 77"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 105.62893392958921,
            "unit": "iter/sec",
            "range": "stddev: 0.00011329414539817254",
            "extra": "mean: 9.467103025640553 msec\nrounds: 117"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 158.72507022771072,
            "unit": "iter/sec",
            "range": "stddev: 0.0018041118565473566",
            "extra": "mean: 6.3002019691368005 msec\nrounds: 162"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 70.29575798118864,
            "unit": "iter/sec",
            "range": "stddev: 0.00027097524368400647",
            "extra": "mean: 14.225609463768825 msec\nrounds: 69"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 56742.35401927269,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015221352218458447",
            "extra": "mean: 17.623519807802605 usec\nrounds: 19563"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 54736.54246538631,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015226143165507991",
            "extra": "mean: 18.269330779019686 usec\nrounds: 16573"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 87875.09497938988,
            "unit": "iter/sec",
            "range": "stddev: 9.343888605105211e-7",
            "extra": "mean: 11.379788553679957 usec\nrounds: 14188"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 53366.403308134075,
            "unit": "iter/sec",
            "range": "stddev: 0.0000075404554785802605",
            "extra": "mean: 18.738381041459107 usec\nrounds: 12828"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 116807.88803573896,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010321919044159757",
            "extra": "mean: 8.561065667877125 usec\nrounds: 23695"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 110377.54295373723,
            "unit": "iter/sec",
            "range": "stddev: 0.000001106831703634025",
            "extra": "mean: 9.059813919024563 usec\nrounds: 20217"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 47011.884864881344,
            "unit": "iter/sec",
            "range": "stddev: 0.00025122459745377453",
            "extra": "mean: 21.27121690343066 usec\nrounds: 12033"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 46965.89469309407,
            "unit": "iter/sec",
            "range": "stddev: 0.000005117115987716872",
            "extra": "mean: 21.292046207884578 usec\nrounds: 11946"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 8528.670155439491,
            "unit": "iter/sec",
            "range": "stddev: 0.00002230136597145028",
            "extra": "mean: 117.25157401734091 usec\nrounds: 3587"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 2423.642143702547,
            "unit": "iter/sec",
            "range": "stddev: 0.00010785494807730589",
            "extra": "mean: 412.6021667837155 usec\nrounds: 1421"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 11130.02391420539,
            "unit": "iter/sec",
            "range": "stddev: 0.0006493518882693265",
            "extra": "mean: 89.84706661085313 usec\nrounds: 4774"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 127.4800063836948,
            "unit": "iter/sec",
            "range": "stddev: 0.003970248761484469",
            "extra": "mean: 7.84436735114491 msec\nrounds: 131"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 98.00462344186758,
            "unit": "iter/sec",
            "range": "stddev: 0.003236041194484391",
            "extra": "mean: 10.203600247422612 msec\nrounds: 97"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 1054.473600484561,
            "unit": "iter/sec",
            "range": "stddev: 0.000026061292215019522",
            "extra": "mean: 948.3404795914008 usec\nrounds: 882"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 227.770872524148,
            "unit": "iter/sec",
            "range": "stddev: 0.00860820630805077",
            "extra": "mean: 4.390377000000214 msec\nrounds: 367"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 134.85486870868363,
            "unit": "iter/sec",
            "range": "stddev: 0.003619997563614907",
            "extra": "mean: 7.415379285713603 msec\nrounds: 133"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 1012.3458160214948,
            "unit": "iter/sec",
            "range": "stddev: 0.0020419794669483643",
            "extra": "mean: 987.80474436096 usec\nrounds: 1064"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 277.63810627279486,
            "unit": "iter/sec",
            "range": "stddev: 0.0064102210063095594",
            "extra": "mean: 3.6018110533337397 msec\nrounds: 450"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "committer": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "distinct": true,
          "id": "c1b92185ff841137b4f82849bbb7a5f9a0bc707e",
          "message": "docs: document the oort-core thin probe\n\n- add OP 0017, the core probe spec and implementation notes\n- update roadmap, conformance, annotation/module docs, README and changelog\n- record the cross-language research behind the scope and dialect boundary\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-20T06:06:33+08:00",
          "tree_id": "8c462818f84c093ebd9f3a3f88e3f8e26f14c9c1",
          "url": "https://github.com/fyabc/oort-lang.py/commit/c1b92185ff841137b4f82849bbb7a5f9a0bc707e"
        },
        "date": 1795126039923,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 21.626116892520898,
            "unit": "iter/sec",
            "range": "stddev: 0.004681539865239575",
            "extra": "mean: 46.24038633333368 msec\nrounds: 6"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.0789109189743806,
            "unit": "iter/sec",
            "range": "stddev: 0.001264467252487006",
            "extra": "mean: 481.021091800001 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 32.11953578405767,
            "unit": "iter/sec",
            "range": "stddev: 0.0013142137185937206",
            "extra": "mean: 31.1337002727276 msec\nrounds: 33"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 29.606925694845575,
            "unit": "iter/sec",
            "range": "stddev: 0.0015164897048197965",
            "extra": "mean: 33.77588103225777 msec\nrounds: 31"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 29.79910261512292,
            "unit": "iter/sec",
            "range": "stddev: 0.0001376166194229307",
            "extra": "mean: 33.55805753333338 msec\nrounds: 30"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 113.86810623094752,
            "unit": "iter/sec",
            "range": "stddev: 0.0011992809372323519",
            "extra": "mean: 8.782090377193049 msec\nrounds: 114"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 35.32015961627496,
            "unit": "iter/sec",
            "range": "stddev: 0.0002017523403626149",
            "extra": "mean: 28.312442833333524 msec\nrounds: 36"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 55.52606263499577,
            "unit": "iter/sec",
            "range": "stddev: 0.0002517081200791505",
            "extra": "mean: 18.009560781818188 msec\nrounds: 55"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 91.53670986381722,
            "unit": "iter/sec",
            "range": "stddev: 0.00025912969489620084",
            "extra": "mean: 10.924578799999907 msec\nrounds: 100"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 114.00364887818347,
            "unit": "iter/sec",
            "range": "stddev: 0.0014989510155495208",
            "extra": "mean: 8.771649064220146 msec\nrounds: 109"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 50.13303085495507,
            "unit": "iter/sec",
            "range": "stddev: 0.00012506260902813476",
            "extra": "mean: 19.946928860000526 msec\nrounds: 50"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 40320.48267144883,
            "unit": "iter/sec",
            "range": "stddev: 0.000001675299054685573",
            "extra": "mean: 24.801290404891557 usec\nrounds: 19979"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 38831.020098444445,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018322888537756301",
            "extra": "mean: 25.752606999888204 usec\nrounds: 16486"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 60425.7299751506,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013138114098087367",
            "extra": "mean: 16.549241530242806 usec\nrounds: 17592"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 42000.09285182781,
            "unit": "iter/sec",
            "range": "stddev: 0.000008481993532233266",
            "extra": "mean: 23.80947117254958 usec\nrounds: 14899"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 81115.48540989263,
            "unit": "iter/sec",
            "range": "stddev: 0.000001240294008975491",
            "extra": "mean: 12.328102272294887 usec\nrounds: 24777"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 75738.99401131786,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012216156467501318",
            "extra": "mean: 13.203238477798736 usec\nrounds: 23650"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 38639.05010367033,
            "unit": "iter/sec",
            "range": "stddev: 0.000006004309985036443",
            "extra": "mean: 25.880553412078054 usec\nrounds: 12441"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 34514.68677552463,
            "unit": "iter/sec",
            "range": "stddev: 0.000008019742086692464",
            "extra": "mean: 28.973173261103707 usec\nrounds: 12738"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 7295.773253961576,
            "unit": "iter/sec",
            "range": "stddev: 0.0000268850261313177",
            "extra": "mean: 137.06566325330957 usec\nrounds: 2539"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1695.9914985817957,
            "unit": "iter/sec",
            "range": "stddev: 0.000566319656536529",
            "extra": "mean: 589.6255970835996 usec\nrounds: 1303"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 8397.315842453016,
            "unit": "iter/sec",
            "range": "stddev: 0.00036303441486374",
            "extra": "mean: 119.08567198871503 usec\nrounds: 8518"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 93.90335982675073,
            "unit": "iter/sec",
            "range": "stddev: 0.0019112684666439071",
            "extra": "mean: 10.649246223404297 msec\nrounds: 94"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 71.52659286742873,
            "unit": "iter/sec",
            "range": "stddev: 0.00011660026816359432",
            "extra": "mean: 13.980814126760578 msec\nrounds: 71"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 750.9157484599041,
            "unit": "iter/sec",
            "range": "stddev: 0.00005170955820883655",
            "extra": "mean: 1.3317073214284785 msec\nrounds: 672"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 212.2712540201994,
            "unit": "iter/sec",
            "range": "stddev: 0.004141018445950682",
            "extra": "mean: 4.7109534666660124 msec\nrounds: 45"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 99.01919132902754,
            "unit": "iter/sec",
            "range": "stddev: 0.0019182497195779932",
            "extra": "mean: 10.099052381443247 msec\nrounds: 97"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 754.3149604432494,
            "unit": "iter/sec",
            "range": "stddev: 0.0013929505050201752",
            "extra": "mean: 1.325706173734618 msec\nrounds: 731"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 251.06689972141106,
            "unit": "iter/sec",
            "range": "stddev: 0.003908610493816504",
            "extra": "mean: 3.98300214448667 msec\nrounds: 263"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "committer": {
            "email": "12120155+fyabc@users.noreply.github.com",
            "name": "fyabc",
            "username": "fyabc"
          },
          "distinct": true,
          "id": "31f316edd6c7ec17c6914e16767d55449bd5007e",
          "message": "feat: support oort-core module imports\n\n- resolve same-dialect core imports with typed module exports\n- support import/from, aliases, namespaces and re-exports\n- cache compiled units and detect circular imports at compile time\n- reject object/core, native and missing-export imports\n- add core module tests, examples and documentation\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-21T11:34:40+08:00",
          "tree_id": "cda2fdab0d79f8abe5b46db105eadde7d468d3bd",
          "url": "https://github.com/fyabc/oort-lang.py/commit/31f316edd6c7ec17c6914e16767d55449bd5007e"
        },
        "date": 1795232208636,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 21.91150739013432,
            "unit": "iter/sec",
            "range": "stddev: 0.0052111288764899975",
            "extra": "mean: 45.63811983333702 msec\nrounds: 6"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.1351800556879468,
            "unit": "iter/sec",
            "range": "stddev: 0.002244213439460808",
            "extra": "mean: 468.3445769999963 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 33.53620695883549,
            "unit": "iter/sec",
            "range": "stddev: 0.0001726642646394886",
            "extra": "mean: 29.81851827272728 msec\nrounds: 33"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 31.090006364132947,
            "unit": "iter/sec",
            "range": "stddev: 0.00019561399235850591",
            "extra": "mean: 32.16467659375111 msec\nrounds: 32"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 29.59948186775326,
            "unit": "iter/sec",
            "range": "stddev: 0.001292401118301963",
            "extra": "mean: 33.784375161290775 msec\nrounds: 31"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 115.44613651493715,
            "unit": "iter/sec",
            "range": "stddev: 0.0013668895555426542",
            "extra": "mean: 8.66204820869526 msec\nrounds: 115"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 36.536557060666624,
            "unit": "iter/sec",
            "range": "stddev: 0.000175366644346751",
            "extra": "mean: 27.369847638888462 msec\nrounds: 36"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 57.07656135787339,
            "unit": "iter/sec",
            "range": "stddev: 0.00023904737138816479",
            "extra": "mean: 17.520326666666925 msec\nrounds: 57"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 93.17116528886281,
            "unit": "iter/sec",
            "range": "stddev: 0.00019887632832766628",
            "extra": "mean: 10.732934346153709 msec\nrounds: 104"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 115.12141210652922,
            "unit": "iter/sec",
            "range": "stddev: 0.0018311308256962577",
            "extra": "mean: 8.686481356523284 msec\nrounds: 115"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 51.28998376464197,
            "unit": "iter/sec",
            "range": "stddev: 0.0002966560821905599",
            "extra": "mean: 19.496984139998403 msec\nrounds: 50"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 40564.47515147999,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015448275254455804",
            "extra": "mean: 24.652112378274303 usec\nrounds: 20956"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 39616.39114013941,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015549066305780744",
            "extra": "mean: 25.24207711052201 usec\nrounds: 16418"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 63534.04406033514,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012846584016638777",
            "extra": "mean: 15.73959307627812 usec\nrounds: 17534"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 42537.30560065057,
            "unit": "iter/sec",
            "range": "stddev: 0.000008694797591972177",
            "extra": "mean: 23.50877625837932 usec\nrounds: 13529"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 84805.9415430369,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010107534693997788",
            "extra": "mean: 11.79162664555201 usec\nrounds: 23929"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 78929.13414448968,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012548501652211779",
            "extra": "mean: 12.6695929309116 usec\nrounds: 20144"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 40526.692966306924,
            "unit": "iter/sec",
            "range": "stddev: 0.000006212894825795313",
            "extra": "mean: 24.675095025182042 usec\nrounds: 8945"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 37348.60401973346,
            "unit": "iter/sec",
            "range": "stddev: 0.000007184161547209741",
            "extra": "mean: 26.774762437483375 usec\nrounds: 13407"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 7463.5802781229995,
            "unit": "iter/sec",
            "range": "stddev: 0.00002692885635166288",
            "extra": "mean: 133.98395444759495 usec\nrounds: 3249"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1691.387236705682,
            "unit": "iter/sec",
            "range": "stddev: 0.0006549378060240435",
            "extra": "mean: 591.230664568394 usec\nrounds: 1112"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 9010.405411040314,
            "unit": "iter/sec",
            "range": "stddev: 0.00041845392256612153",
            "extra": "mean: 110.98279759695552 usec\nrounds: 10820"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 96.61152399928115,
            "unit": "iter/sec",
            "range": "stddev: 0.003013286561580843",
            "extra": "mean: 10.350732072163986 msec\nrounds: 97"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 73.42991090711885,
            "unit": "iter/sec",
            "range": "stddev: 0.00007814405403503952",
            "extra": "mean: 13.618428616437996 msec\nrounds: 73"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 780.2634321900135,
            "unit": "iter/sec",
            "range": "stddev: 0.00003776649676854484",
            "extra": "mean: 1.2816184364724594 msec\nrounds: 669"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 226.6827967233777,
            "unit": "iter/sec",
            "range": "stddev: 0.005050013985726717",
            "extra": "mean: 4.41145077815634 msec\nrounds: 293"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 101.8508363518557,
            "unit": "iter/sec",
            "range": "stddev: 0.002254701739106261",
            "extra": "mean: 9.81827971000044 msec\nrounds: 100"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 748.7985475917029,
            "unit": "iter/sec",
            "range": "stddev: 0.0018819421235867593",
            "extra": "mean: 1.3354726758167665 msec\nrounds: 765"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 241.47985661878556,
            "unit": "iter/sec",
            "range": "stddev: 0.00505496158808478",
            "extra": "mean: 4.141132159021692 msec\nrounds: 327"
          }
        ]
      }
    ]
  }
}