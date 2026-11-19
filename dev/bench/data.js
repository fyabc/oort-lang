window.BENCHMARK_DATA = {
  "lastUpdate": 1795118210160,
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
      }
    ]
  }
}