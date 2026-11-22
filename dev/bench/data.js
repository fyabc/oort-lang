window.BENCHMARK_DATA = {
  "lastUpdate": 1795354558512,
  "repoUrl": "https://github.com/fyabc/oort-lang",
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
          "id": "86f8fdf57c73f6fd0048a0bf52f0f9ec4ee9997c",
          "message": "docs: document oort-core ADTs and match\n\n- add ADT/match sections to spec 11, conformance and implementation notes\n- update OP 0017/0005/0010, roadmap, README and changelog\n- note keyword/token changes and deferred generic ADTs\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-21T12:30:42+08:00",
          "tree_id": "70b189b0d2ec38670b4fce35f4baae97c1aca080",
          "url": "https://github.com/fyabc/oort-lang.py/commit/86f8fdf57c73f6fd0048a0bf52f0f9ec4ee9997c"
        },
        "date": 1795235490631,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 23.683759502056777,
            "unit": "iter/sec",
            "range": "stddev: 0.004014918358443497",
            "extra": "mean: 42.223026285719406 msec\nrounds: 7"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.7228538641739206,
            "unit": "iter/sec",
            "range": "stddev: 0.0014499301493435886",
            "extra": "mean: 367.2617223999964 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 43.729487422977336,
            "unit": "iter/sec",
            "range": "stddev: 0.00027754215171626475",
            "extra": "mean: 22.867864659089452 msec\nrounds: 44"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 40.34700534449006,
            "unit": "iter/sec",
            "range": "stddev: 0.00022044423094738413",
            "extra": "mean: 24.784986926831827 msec\nrounds: 41"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 38.24503960200829,
            "unit": "iter/sec",
            "range": "stddev: 0.00017942695321270508",
            "extra": "mean: 26.147181710526684 msec\nrounds: 38"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 153.26410649426572,
            "unit": "iter/sec",
            "range": "stddev: 0.00006637662879369786",
            "extra": "mean: 6.524684891158221 msec\nrounds: 147"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 46.52599921890862,
            "unit": "iter/sec",
            "range": "stddev: 0.00019604673800092997",
            "extra": "mean: 21.493358913043828 msec\nrounds: 46"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 74.46130725016098,
            "unit": "iter/sec",
            "range": "stddev: 0.00011370979267848185",
            "extra": "mean: 13.429793767122428 msec\nrounds: 73"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 100.89308853870591,
            "unit": "iter/sec",
            "range": "stddev: 0.0001340381630897669",
            "extra": "mean: 9.911481692984026 msec\nrounds: 114"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 152.57997665627306,
            "unit": "iter/sec",
            "range": "stddev: 0.0014835104138646064",
            "extra": "mean: 6.553939919998584 msec\nrounds: 150"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 67.15630156551912,
            "unit": "iter/sec",
            "range": "stddev: 0.00015288277153820097",
            "extra": "mean: 14.890635378786886 msec\nrounds: 66"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 52624.512454370844,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013099586438850274",
            "extra": "mean: 19.0025513465245 usec\nrounds: 23390"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 52041.45753620283,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011543493307750672",
            "extra": "mean: 19.215449515501103 usec\nrounds: 22918"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 83191.30795589957,
            "unit": "iter/sec",
            "range": "stddev: 9.424159995969549e-7",
            "extra": "mean: 12.020486569703998 usec\nrounds: 23119"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 53387.62872730445,
            "unit": "iter/sec",
            "range": "stddev: 0.000006977611720532826",
            "extra": "mean: 18.730931188344055 usec\nrounds: 17904"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 112096.650282365,
            "unit": "iter/sec",
            "range": "stddev: 7.907409859415138e-7",
            "extra": "mean: 8.920873170438703 usec\nrounds: 34913"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 106222.47705748797,
            "unit": "iter/sec",
            "range": "stddev: 8.480774233461287e-7",
            "extra": "mean: 9.414203356026018 usec\nrounds: 28128"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 50934.57313728318,
            "unit": "iter/sec",
            "range": "stddev: 0.00000458080858290985",
            "extra": "mean: 19.63302995206645 usec\nrounds: 16927"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 42384.96444690899,
            "unit": "iter/sec",
            "range": "stddev: 0.00014770892908813903",
            "extra": "mean: 23.59327212017815 usec\nrounds: 17518"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 8176.273963785234,
            "unit": "iter/sec",
            "range": "stddev: 0.00002147932054345341",
            "extra": "mean: 122.30509941683101 usec\nrounds: 3772"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 2210.658434613067,
            "unit": "iter/sec",
            "range": "stddev: 0.00010596642731889984",
            "extra": "mean: 452.35391607434394 usec\nrounds: 1406"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 11133.971792520364,
            "unit": "iter/sec",
            "range": "stddev: 0.0002973825824226895",
            "extra": "mean: 89.81520868157624 usec\nrounds: 13154"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 125.42001658508855,
            "unit": "iter/sec",
            "range": "stddev: 0.001935099818902033",
            "extra": "mean: 7.973208960003376 msec\nrounds: 125"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 95.97303457163028,
            "unit": "iter/sec",
            "range": "stddev: 0.00006643769624792371",
            "extra": "mean: 10.419593425001494 msec\nrounds: 40"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 1001.496693661114,
            "unit": "iter/sec",
            "range": "stddev: 0.000026496129553123795",
            "extra": "mean: 998.5055430830805 usec\nrounds: 882"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 323.35507371431567,
            "unit": "iter/sec",
            "range": "stddev: 0.003131664947242752",
            "extra": "mean: 3.0925755656566576 msec\nrounds: 396"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 134.36512783555202,
            "unit": "iter/sec",
            "range": "stddev: 0.0012369566794179076",
            "extra": "mean: 7.442407238460628 msec\nrounds: 130"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 1116.5828017657777,
            "unit": "iter/sec",
            "range": "stddev: 0.0008171528901862859",
            "extra": "mean: 895.589649436287 usec\nrounds: 1064"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 354.75605547781345,
            "unit": "iter/sec",
            "range": "stddev: 0.002765559864355622",
            "extra": "mean: 2.8188384230767283 msec\nrounds: 442"
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
          "id": "b5a951a8d6c29494e0e05adc499c72d67ad1e5b3",
          "message": "docs: document core function values and currying\n\n- document function type syntax, right-associative arrows and chained calls\n- note that multi-argument functions are not automatically curried\n- update spec, conformance, implementation notes, roadmap, README and changelog\n- add function value and currying examples to the examples index\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-21T12:56:12+08:00",
          "tree_id": "50bb2d2ad5a73dcce286ef25fda2ec3e06377ea6",
          "url": "https://github.com/fyabc/oort-lang.py/commit/b5a951a8d6c29494e0e05adc499c72d67ad1e5b3"
        },
        "date": 1795237025430,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 16.126847850512014,
            "unit": "iter/sec",
            "range": "stddev: 0.005742558422144803",
            "extra": "mean: 62.0083980000004 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.3607059584173677,
            "unit": "iter/sec",
            "range": "stddev: 0.015595677094158563",
            "extra": "mean: 734.9126339999984 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 20.907424350238554,
            "unit": "iter/sec",
            "range": "stddev: 0.0012922559973819034",
            "extra": "mean: 47.82989923809482 msec\nrounds: 21"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 18.916206727728326,
            "unit": "iter/sec",
            "range": "stddev: 0.00196585990267557",
            "extra": "mean: 52.86472147368477 msec\nrounds: 19"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 17.870618065502367,
            "unit": "iter/sec",
            "range": "stddev: 0.0011551016554070977",
            "extra": "mean: 55.95777361111035 msec\nrounds: 18"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 83.27269024747983,
            "unit": "iter/sec",
            "range": "stddev: 0.0016805944514228616",
            "extra": "mean: 12.008738963855729 msec\nrounds: 83"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 21.586570631756228,
            "unit": "iter/sec",
            "range": "stddev: 0.0005623366851116161",
            "extra": "mean: 46.32509799999865 msec\nrounds: 21"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 35.59603244151622,
            "unit": "iter/sec",
            "range": "stddev: 0.0005132346194018647",
            "extra": "mean: 28.09301855882354 msec\nrounds: 34"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 62.77944407228119,
            "unit": "iter/sec",
            "range": "stddev: 0.0002395388828132919",
            "extra": "mean: 15.928780746268616 msec\nrounds: 67"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 82.29765417718264,
            "unit": "iter/sec",
            "range": "stddev: 0.0022779531483635824",
            "extra": "mean: 12.151014630952314 msec\nrounds: 84"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 32.06806533451018,
            "unit": "iter/sec",
            "range": "stddev: 0.0010125626228195093",
            "extra": "mean: 31.183671031250082 msec\nrounds: 32"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 29906.220213640867,
            "unit": "iter/sec",
            "range": "stddev: 0.000002549257390697386",
            "extra": "mean: 33.43785984508596 usec\nrounds: 14591"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 26561.8740350078,
            "unit": "iter/sec",
            "range": "stddev: 0.00000292544092769068",
            "extra": "mean: 37.647946025270215 usec\nrounds: 13284"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 35820.26159835976,
            "unit": "iter/sec",
            "range": "stddev: 0.000002727812063290136",
            "extra": "mean: 27.917160717938224 usec\nrounds: 14653"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 24575.14155077312,
            "unit": "iter/sec",
            "range": "stddev: 0.000010098042488362159",
            "extra": "mean: 40.69152553746086 usec\nrounds: 12511"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 61257.768683479306,
            "unit": "iter/sec",
            "range": "stddev: 0.000001976640295931222",
            "extra": "mean: 16.324460088760812 usec\nrounds: 22763"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 55768.61793869744,
            "unit": "iter/sec",
            "range": "stddev: 0.0000022172548069390856",
            "extra": "mean: 17.93123152342112 usec\nrounds: 16115"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 23245.450044855206,
            "unit": "iter/sec",
            "range": "stddev: 0.000009989956419885103",
            "extra": "mean: 43.019171410764955 usec\nrounds: 9626"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 20979.44955309006,
            "unit": "iter/sec",
            "range": "stddev: 0.000010893993073719966",
            "extra": "mean: 47.66569291865478 usec\nrounds: 8939"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 4355.6542669806,
            "unit": "iter/sec",
            "range": "stddev: 0.000037242451364897024",
            "extra": "mean: 229.5866335353595 usec\nrounds: 2475"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1239.0917598156964,
            "unit": "iter/sec",
            "range": "stddev: 0.0007673914176530738",
            "extra": "mean: 807.0427327744807 usec\nrounds: 1074"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 6840.678526458207,
            "unit": "iter/sec",
            "range": "stddev: 0.0004489024800674863",
            "extra": "mean: 146.1843289568754 usec\nrounds: 8302"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 68.48705655359987,
            "unit": "iter/sec",
            "range": "stddev: 0.00029010215550893676",
            "extra": "mean: 14.601299140624802 msec\nrounds: 64"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 47.78363347906008,
            "unit": "iter/sec",
            "range": "stddev: 0.003377321889459715",
            "extra": "mean: 20.927667638297613 msec\nrounds: 47"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 535.6748892721075,
            "unit": "iter/sec",
            "range": "stddev: 0.00007814258580686104",
            "extra": "mean: 1.8668039514766739 msec\nrounds: 474"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 171.6514090074965,
            "unit": "iter/sec",
            "range": "stddev: 0.006418612150645357",
            "extra": "mean: 5.825760509523852 msec\nrounds: 210"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 72.27749302748842,
            "unit": "iter/sec",
            "range": "stddev: 0.0032811383481922687",
            "extra": "mean: 13.835565652777722 msec\nrounds: 72"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 582.7971212516183,
            "unit": "iter/sec",
            "range": "stddev: 0.0015350335783521263",
            "extra": "mean: 1.7158629710668347 msec\nrounds: 553"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 184.34594201633269,
            "unit": "iter/sec",
            "range": "stddev: 0.004494964965376489",
            "extra": "mean: 5.424583742187295 msec\nrounds: 256"
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
          "id": "95f666b7c0cdd59317ff01834c11b7a3ed8741c8",
          "message": "docs: close the 0.3.1 review findings\n\n- Replace stale host-equality statements in spec/02 and document container\n  ordering, special-method restrictions, and zip's eager draining.\n- Record the 0.3.1 release decision in OP 0016 D5, add the equality/ordering\n  follow-up, and list OP 0016 in the roadmap.\n- Update interpreter/equality notes, README and CHANGELOG.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-21T13:35:25+08:00",
          "tree_id": "fd49d896ebbe69e4b7d2db1c248a8a7cb56b97f6",
          "url": "https://github.com/fyabc/oort-lang.py/commit/95f666b7c0cdd59317ff01834c11b7a3ed8741c8"
        },
        "date": 1795239379109,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 36.337474967294895,
            "unit": "iter/sec",
            "range": "stddev: 0.00425052932141907",
            "extra": "mean: 27.519798800000217 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.1107071640209467,
            "unit": "iter/sec",
            "range": "stddev: 0.004002238192554459",
            "extra": "mean: 473.77486420000423 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 31.964825937502905,
            "unit": "iter/sec",
            "range": "stddev: 0.000269833737233775",
            "extra": "mean: 31.284387468750285 msec\nrounds: 32"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 28.697505108573093,
            "unit": "iter/sec",
            "range": "stddev: 0.00026130133643866254",
            "extra": "mean: 34.84623475861879 msec\nrounds: 29"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 26.451498448192957,
            "unit": "iter/sec",
            "range": "stddev: 0.0004593573734234396",
            "extra": "mean: 37.80504162962894 msec\nrounds: 27"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 116.18621381231945,
            "unit": "iter/sec",
            "range": "stddev: 0.00010533959865560304",
            "extra": "mean: 8.606873115043948 msec\nrounds: 113"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 33.855103812036674,
            "unit": "iter/sec",
            "range": "stddev: 0.00042936988960177606",
            "extra": "mean: 29.537643882352093 msec\nrounds: 34"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 54.3970602794092,
            "unit": "iter/sec",
            "range": "stddev: 0.0001725102072790662",
            "extra": "mean: 18.383346358489298 msec\nrounds: 53"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 163.07485275547907,
            "unit": "iter/sec",
            "range": "stddev: 0.0002352043447802639",
            "extra": "mean: 6.132153321637149 msec\nrounds: 171"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 114.68398766783501,
            "unit": "iter/sec",
            "range": "stddev: 0.001670209955354372",
            "extra": "mean: 8.719613089286275 msec\nrounds: 112"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 49.23531508953797,
            "unit": "iter/sec",
            "range": "stddev: 0.00019989664926087626",
            "extra": "mean: 20.310624562500063 msec\nrounds: 48"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 41404.104588633185,
            "unit": "iter/sec",
            "range": "stddev: 0.000001891480398508266",
            "extra": "mean: 24.15219481100754 usec\nrounds: 17807"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 39574.08851747106,
            "unit": "iter/sec",
            "range": "stddev: 0.000002342358103622061",
            "extra": "mean: 25.269059565541802 usec\nrounds: 18232"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 56883.20143295274,
            "unit": "iter/sec",
            "range": "stddev: 0.000001766539280757601",
            "extra": "mean: 17.57988254544152 usec\nrounds: 14976"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 35229.23436228926,
            "unit": "iter/sec",
            "range": "stddev: 0.000008647752502129079",
            "extra": "mean: 28.38551612323539 usec\nrounds: 11164"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 83312.99914793875,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015250332214283278",
            "extra": "mean: 12.002928837363081 usec\nrounds: 26053"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 78490.08359077743,
            "unit": "iter/sec",
            "range": "stddev: 0.000001410900837184891",
            "extra": "mean: 12.740462925401951 usec\nrounds: 20742"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 34582.87741472659,
            "unit": "iter/sec",
            "range": "stddev: 0.0000056545023470707255",
            "extra": "mean: 28.916043856262966 usec\nrounds: 12655"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 31059.05554866767,
            "unit": "iter/sec",
            "range": "stddev: 0.000007278444529531008",
            "extra": "mean: 32.19672917719794 usec\nrounds: 7972"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 6777.846680208029,
            "unit": "iter/sec",
            "range": "stddev: 0.00002463877889367735",
            "extra": "mean: 147.53948373014944 usec\nrounds: 2981"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1854.5672254985657,
            "unit": "iter/sec",
            "range": "stddev: 0.000601881187544233",
            "extra": "mean: 539.2093563667765 usec\nrounds: 1288"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 9834.459079026328,
            "unit": "iter/sec",
            "range": "stddev: 0.0004407431179851149",
            "extra": "mean: 101.68327428731405 usec\nrounds: 4138"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 91.98561028959041,
            "unit": "iter/sec",
            "range": "stddev: 0.0026223900197353328",
            "extra": "mean: 10.871265590909118 msec\nrounds: 88"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 70.75677991792834,
            "unit": "iter/sec",
            "range": "stddev: 0.0001102021943317012",
            "extra": "mean: 14.132921271430275 msec\nrounds: 70"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 754.8080850645406,
            "unit": "iter/sec",
            "range": "stddev: 0.00003504075730306651",
            "extra": "mean: 1.3248400749635507 msec\nrounds: 667"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 257.0374037794212,
            "unit": "iter/sec",
            "range": "stddev: 0.0051387373605982275",
            "extra": "mean: 3.8904843625722205 msec\nrounds: 342"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 98.72691261667632,
            "unit": "iter/sec",
            "range": "stddev: 0.0023009564041375297",
            "extra": "mean: 10.128950389471475 msec\nrounds: 95"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 867.849264374173,
            "unit": "iter/sec",
            "range": "stddev: 0.001701170730220073",
            "extra": "mean: 1.1522738349281474 msec\nrounds: 836"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 1939.2284008180868,
            "unit": "iter/sec",
            "range": "stddev: 0.000018700058732517927",
            "extra": "mean: 515.6690153558694 usec\nrounds: 1628"
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
          "id": "afb329da924907b246a99b5e881b01973c0a1699",
          "message": "docs: document oort-core Float and String scalars\n\n- Update the core probe spec with Float/String types, numeric promotion,\n  `/` versus `//`, String operators and the remaining rejection list.\n- Align the conformance matrix, type-checker notes, roadmap, OP 0017 and\n  index/README/CHANGELOG with the scalar slice.\n- Add the scalar example to the examples page.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-21T13:52:16+08:00",
          "tree_id": "4e2b74ba3c8c390488961dc98b91be2a8f80952a",
          "url": "https://github.com/fyabc/oort-lang.py/commit/afb329da924907b246a99b5e881b01973c0a1699"
        },
        "date": 1795240381280,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 21.204753438477944,
            "unit": "iter/sec",
            "range": "stddev: 0.005813157007614127",
            "extra": "mean: 47.15923733333346 msec\nrounds: 6"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.096525272223625,
            "unit": "iter/sec",
            "range": "stddev: 0.00512985815760688",
            "extra": "mean: 476.9797022000006 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 32.71917060614653,
            "unit": "iter/sec",
            "range": "stddev: 0.00015827059448878",
            "extra": "mean: 30.563121909090906 msec\nrounds: 33"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 30.60081898728909,
            "unit": "iter/sec",
            "range": "stddev: 0.0003072174626603567",
            "extra": "mean: 32.67886393548415 msec\nrounds: 31"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 29.576649160559676,
            "unit": "iter/sec",
            "range": "stddev: 0.0003287995638912524",
            "extra": "mean: 33.8104561666673 msec\nrounds: 30"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 111.56467304862817,
            "unit": "iter/sec",
            "range": "stddev: 0.0014336017338299947",
            "extra": "mean: 8.963410842105242 msec\nrounds: 114"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 35.478720046177635,
            "unit": "iter/sec",
            "range": "stddev: 0.0001421790352439152",
            "extra": "mean: 28.185909714286236 msec\nrounds: 35"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 56.20676761939147,
            "unit": "iter/sec",
            "range": "stddev: 0.00017511992068620254",
            "extra": "mean: 17.79145185454496 msec\nrounds: 55"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 89.52378562762547,
            "unit": "iter/sec",
            "range": "stddev: 0.0017836616243489996",
            "extra": "mean: 11.170215747572426 msec\nrounds: 103"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 112.94881631452613,
            "unit": "iter/sec",
            "range": "stddev: 0.001986675581049123",
            "extra": "mean: 8.853567771930619 msec\nrounds: 114"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 51.046198647442296,
            "unit": "iter/sec",
            "range": "stddev: 0.00012193113601652679",
            "extra": "mean: 19.590097333332103 msec\nrounds: 51"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 40144.46942909481,
            "unit": "iter/sec",
            "range": "stddev: 0.000003221506836334592",
            "extra": "mean: 24.910031549084252 usec\nrounds: 19430"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 38712.74260066743,
            "unit": "iter/sec",
            "range": "stddev: 0.0000034508745569981173",
            "extra": "mean: 25.831287912491103 usec\nrounds: 16637"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 63010.15316176451,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013539560685287753",
            "extra": "mean: 15.870458169379832 usec\nrounds: 17786"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 42570.58429814011,
            "unit": "iter/sec",
            "range": "stddev: 0.000008324652814718493",
            "extra": "mean: 23.490398745682462 usec\nrounds: 12118"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 83985.04786599572,
            "unit": "iter/sec",
            "range": "stddev: 9.678219355963094e-7",
            "extra": "mean: 11.90688134863688 usec\nrounds: 25596"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 79402.18980364826,
            "unit": "iter/sec",
            "range": "stddev: 0.000001062140944774181",
            "extra": "mean: 12.594111100372366 usec\nrounds: 20720"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 39797.477644165265,
            "unit": "iter/sec",
            "range": "stddev: 0.000006701008967405963",
            "extra": "mean: 25.127220597776017 usec\nrounds: 12380"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 36707.725724738164,
            "unit": "iter/sec",
            "range": "stddev: 0.0000072157598824596665",
            "extra": "mean: 27.242221637448853 usec\nrounds: 12349"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 7425.429049279952,
            "unit": "iter/sec",
            "range": "stddev: 0.00002712407906865319",
            "extra": "mean: 134.67235271704206 usec\nrounds: 3147"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1804.9507441314186,
            "unit": "iter/sec",
            "range": "stddev: 0.0006931728893557037",
            "extra": "mean: 554.0317392324308 usec\nrounds: 1277"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 8577.481490151871,
            "unit": "iter/sec",
            "range": "stddev: 0.0006469417568771829",
            "extra": "mean: 116.58433785583071 usec\nrounds: 11277"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 96.07527049614755,
            "unit": "iter/sec",
            "range": "stddev: 0.003087094562855613",
            "extra": "mean: 10.408505693877784 msec\nrounds: 98"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 72.64396800015358,
            "unit": "iter/sec",
            "range": "stddev: 0.00008507500225934051",
            "extra": "mean: 13.76576786110976 msec\nrounds: 72"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 770.2589838572521,
            "unit": "iter/sec",
            "range": "stddev: 0.00008156787443086737",
            "extra": "mean: 1.2982646369046758 msec\nrounds: 672"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 207.26094895846785,
            "unit": "iter/sec",
            "range": "stddev: 0.0061624804429662545",
            "extra": "mean: 4.824835575757137 msec\nrounds: 264"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 98.80066896690796,
            "unit": "iter/sec",
            "range": "stddev: 0.0029432388694770983",
            "extra": "mean: 10.121388958762388 msec\nrounds: 97"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 715.827687023941,
            "unit": "iter/sec",
            "range": "stddev: 0.0018389537683121333",
            "extra": "mean: 1.3969842437326048 msec\nrounds: 718"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 1636.5688747626152,
            "unit": "iter/sec",
            "range": "stddev: 0.00001469835671114322",
            "extra": "mean: 611.0344730496297 usec\nrounds: 1410"
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
          "id": "d5fc4d50696efd9ebddd9fed7129936aa4d55d58",
          "message": "editor: release VSCode grammar 0.1.3 with enum names\n\n- Highlight `enum` declarations and their type names, matching the existing\n  `class` rule.\n- Cover `enum`, `match`, `=>` and `Unit` scopes with example-like snippets.\n- Bump the extension to 0.1.3 and update the packaging instructions.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-21T14:38:30+08:00",
          "tree_id": "f58b63e7aa5b467b03982bded7ccc05e77a8ff30",
          "url": "https://github.com/fyabc/oort-lang.py/commit/d5fc4d50696efd9ebddd9fed7129936aa4d55d58"
        },
        "date": 1795243163195,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 24.97764884014109,
            "unit": "iter/sec",
            "range": "stddev: 0.004379485291126865",
            "extra": "mean: 40.035793857143176 msec\nrounds: 7"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.9047765650862427,
            "unit": "iter/sec",
            "range": "stddev: 0.0008073383534268005",
            "extra": "mean: 344.2605575999991 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 44.82294336742394,
            "unit": "iter/sec",
            "range": "stddev: 0.0009636996227645717",
            "extra": "mean: 22.310002977777938 msec\nrounds: 45"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 42.73681513403866,
            "unit": "iter/sec",
            "range": "stddev: 0.0019574303185812057",
            "extra": "mean: 23.399029545454553 msec\nrounds: 44"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 41.6854007410419,
            "unit": "iter/sec",
            "range": "stddev: 0.0027633967062311252",
            "extra": "mean: 23.989214022727076 msec\nrounds: 44"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 168.8445392992129,
            "unit": "iter/sec",
            "range": "stddev: 0.00015003375044865728",
            "extra": "mean: 5.922607886227692 msec\nrounds: 167"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 50.91086066687628,
            "unit": "iter/sec",
            "range": "stddev: 0.0012583621800949447",
            "extra": "mean: 19.642174319999697 msec\nrounds: 50"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 78.87685201612852,
            "unit": "iter/sec",
            "range": "stddev: 0.0005473848234083396",
            "extra": "mean: 12.67799074683562 msec\nrounds: 79"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 107.8790982286761,
            "unit": "iter/sec",
            "range": "stddev: 0.00015420991557530962",
            "extra": "mean: 9.2696362540986 msec\nrounds: 122"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 164.99246548323933,
            "unit": "iter/sec",
            "range": "stddev: 0.0015759302082486613",
            "extra": "mean: 6.060882823171004 msec\nrounds: 164"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 69.61798098179963,
            "unit": "iter/sec",
            "range": "stddev: 0.0017041736444921136",
            "extra": "mean: 14.364105162162517 msec\nrounds: 74"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 57442.32885408039,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012144489186530823",
            "extra": "mean: 17.408764929087056 usec\nrounds: 23980"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 55578.01709185427,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013604932118483191",
            "extra": "mean: 17.99272540341429 usec\nrounds: 23489"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 86182.38709240354,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010994458536902925",
            "extra": "mean: 11.60329893076429 usec\nrounds: 17770"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 49254.82355340742,
            "unit": "iter/sec",
            "range": "stddev: 0.000006345301609112392",
            "extra": "mean: 20.30258008975896 usec\nrounds: 13591"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 110849.80535861281,
            "unit": "iter/sec",
            "range": "stddev: 0.000006497698200680717",
            "extra": "mean: 9.021215659918179 usec\nrounds: 32695"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 115171.2269131153,
            "unit": "iter/sec",
            "range": "stddev: 7.098179746967378e-7",
            "extra": "mean: 8.68272420814268 usec\nrounds: 27499"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 47668.04521176671,
            "unit": "iter/sec",
            "range": "stddev: 0.00014638567797624471",
            "extra": "mean: 20.97841427223353 usec\nrounds: 15905"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 40862.32868055999,
            "unit": "iter/sec",
            "range": "stddev: 0.000006183972447109984",
            "extra": "mean: 24.472418295527635 usec\nrounds: 15348"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 8729.135156354245,
            "unit": "iter/sec",
            "range": "stddev: 0.00002036881452700651",
            "extra": "mean: 114.55888608530304 usec\nrounds: 2695"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 2522.636591093322,
            "unit": "iter/sec",
            "range": "stddev: 0.00009509966529061525",
            "extra": "mean: 396.4106457230907 usec\nrounds: 1321"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 11685.568660248413,
            "unit": "iter/sec",
            "range": "stddev: 0.0005021219076900607",
            "extra": "mean: 85.5756385567925 usec\nrounds: 14218"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 130.46851914836773,
            "unit": "iter/sec",
            "range": "stddev: 0.0029300529460644644",
            "extra": "mean: 7.664684220588172 msec\nrounds: 136"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 103.85456521277155,
            "unit": "iter/sec",
            "range": "stddev: 0.00012435932804664583",
            "extra": "mean: 9.62884970873697 msec\nrounds: 103"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 1044.3685886131796,
            "unit": "iter/sec",
            "range": "stddev: 0.00091921276764688",
            "extra": "mean: 957.5163509349734 usec\nrounds: 909"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 300.13567553424747,
            "unit": "iter/sec",
            "range": "stddev: 0.005198864276750108",
            "extra": "mean: 3.331826508861301 msec\nrounds: 395"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 138.16550116434914,
            "unit": "iter/sec",
            "range": "stddev: 0.0023017181692059204",
            "extra": "mean: 7.23769675912434 msec\nrounds: 137"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 1059.7019023393818,
            "unit": "iter/sec",
            "range": "stddev: 0.002153928071004871",
            "extra": "mean: 943.6616069032387 usec\nrounds: 1043"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 2287.5529681337994,
            "unit": "iter/sec",
            "range": "stddev: 0.00001562814951185349",
            "extra": "mean: 437.14834757063863 usec\nrounds: 1873"
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
          "id": "1d7ddf531c1318ef514f07ebf6201cf192a27690",
          "message": "docs: document subscript and missing-attribute protocols\n\n- Add OP 0018 with the cross-language survey, `operator \"[]\"`/`\"[]=\"` and\n  `on_missing` decisions, alternatives and deferred follow-ups.\n- Update the expression/class specs, conformance matrix, interpreter and\n  class notes, registration, roadmap, README and CHANGELOG.\n- Register the new protocol example on the examples page.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-21T15:09:33+08:00",
          "tree_id": "3821fa3a237bddd7c2436464e9492a27fd615e11",
          "url": "https://github.com/fyabc/oort-lang.py/commit/1d7ddf531c1318ef514f07ebf6201cf192a27690"
        },
        "date": 1795245852282,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 15.5589584934006,
            "unit": "iter/sec",
            "range": "stddev: 0.0060560404737520935",
            "extra": "mean: 64.27165420000023 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.3650333320473105,
            "unit": "iter/sec",
            "range": "stddev: 0.009424362266311865",
            "extra": "mean: 732.5828435999988 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 20.911255996264202,
            "unit": "iter/sec",
            "range": "stddev: 0.0006952590494205625",
            "extra": "mean: 47.82113519047589 msec\nrounds: 21"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 18.843371203950724,
            "unit": "iter/sec",
            "range": "stddev: 0.0008939991151450769",
            "extra": "mean: 53.06906015789462 msec\nrounds: 19"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 17.583890987956828,
            "unit": "iter/sec",
            "range": "stddev: 0.001855847174901101",
            "extra": "mean: 56.8702342777772 msec\nrounds: 18"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 81.63443293456565,
            "unit": "iter/sec",
            "range": "stddev: 0.0016224864837349816",
            "extra": "mean: 12.249732913580148 msec\nrounds: 81"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 21.362240831558633,
            "unit": "iter/sec",
            "range": "stddev: 0.0011451716582704732",
            "extra": "mean: 46.811568499999815 msec\nrounds: 22"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 35.25368005363574,
            "unit": "iter/sec",
            "range": "stddev: 0.00032377162276089335",
            "extra": "mean: 28.36583297058853 msec\nrounds: 34"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 61.16824520074814,
            "unit": "iter/sec",
            "range": "stddev: 0.0003348287276764736",
            "extra": "mean: 16.348351938462496 msec\nrounds: 65"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 82.14157739192599,
            "unit": "iter/sec",
            "range": "stddev: 0.002113850316603141",
            "extra": "mean: 12.17410271084341 msec\nrounds: 83"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 31.771507679846838,
            "unit": "iter/sec",
            "range": "stddev: 0.00037778211421110835",
            "extra": "mean: 31.47474177419398 msec\nrounds: 31"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 29003.155002787116,
            "unit": "iter/sec",
            "range": "stddev: 0.0000055468862930209085",
            "extra": "mean: 34.47900753914197 usec\nrounds: 13662"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 26176.230425811624,
            "unit": "iter/sec",
            "range": "stddev: 0.000003094624719798782",
            "extra": "mean: 38.202597690075685 usec\nrounds: 13507"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 34683.617733314524,
            "unit": "iter/sec",
            "range": "stddev: 0.000003186178744777205",
            "extra": "mean: 28.832055747156787 usec\nrounds: 14207"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 22027.714694395112,
            "unit": "iter/sec",
            "range": "stddev: 0.000011113586470198114",
            "extra": "mean: 45.39735573452143 usec\nrounds: 10803"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 60395.85646310412,
            "unit": "iter/sec",
            "range": "stddev: 0.000002867064235203139",
            "extra": "mean: 16.55742725680032 usec\nrounds: 20538"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 54442.083569662296,
            "unit": "iter/sec",
            "range": "stddev: 0.000002301917416600894",
            "extra": "mean: 18.36814343669329 usec\nrounds: 13065"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 22768.456568854515,
            "unit": "iter/sec",
            "range": "stddev: 0.000009109290014172468",
            "extra": "mean: 43.92041230269084 usec\nrounds: 9949"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 20356.96955743468,
            "unit": "iter/sec",
            "range": "stddev: 0.00000841905036802744",
            "extra": "mean: 49.123225201994 usec\nrounds: 8912"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 4381.275999462629,
            "unit": "iter/sec",
            "range": "stddev: 0.00003523772702268185",
            "extra": "mean: 228.24400930748297 usec\nrounds: 2686"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1299.8092759624044,
            "unit": "iter/sec",
            "range": "stddev: 0.0007677245686298471",
            "extra": "mean: 769.3436402502823 usec\nrounds: 959"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 6793.439046559673,
            "unit": "iter/sec",
            "range": "stddev: 0.00045779374356252645",
            "extra": "mean: 147.20084969429718 usec\nrounds: 8343"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 66.17895801869861,
            "unit": "iter/sec",
            "range": "stddev: 0.0035193225434116348",
            "extra": "mean: 15.110543138461834 msec\nrounds: 65"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 48.64598345298229,
            "unit": "iter/sec",
            "range": "stddev: 0.00035818897924579763",
            "extra": "mean: 20.556681744681512 msec\nrounds: 47"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 527.1773878412181,
            "unit": "iter/sec",
            "range": "stddev: 0.00010953792340843274",
            "extra": "mean: 1.8968947133620089 msec\nrounds: 464"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 196.3170485433078,
            "unit": "iter/sec",
            "range": "stddev: 0.004436710079772128",
            "extra": "mean: 5.093801111111339 msec\nrounds: 36"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 73.4608143533491,
            "unit": "iter/sec",
            "range": "stddev: 0.0025543174772042344",
            "extra": "mean: 13.612699624999594 msec\nrounds: 72"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 573.8305133501252,
            "unit": "iter/sec",
            "range": "stddev: 0.0015601655366255288",
            "extra": "mean: 1.7426748434164314 msec\nrounds: 562"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 1098.2924713690227,
            "unit": "iter/sec",
            "range": "stddev: 0.00004445654104682984",
            "extra": "mean: 910.504283757403 usec\nrounds: 1022"
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
          "id": "5ff200ee394feb426f06dec6640840c17a711f3b",
          "message": "docs: record the first HIR/bytecode/VM slice\n\n- Turn OP 0004 into an accepted, in-progress proposal with the HIR, bytecode\n  and VM decisions, current limitations and benchmark numbers.\n- Record the VM speedups and remaining subset in the HIR and performance\n  design notes; update README, roadmap, benchmark/test indexes and CHANGELOG.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-21T16:13:14+08:00",
          "tree_id": "d272431eeb664c5a21cada085bb069e9a70d711e",
          "url": "https://github.com/fyabc/oort-lang.py/commit/5ff200ee394feb426f06dec6640840c17a711f3b"
        },
        "date": 1795249080230,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 29.196847326094215,
            "unit": "iter/sec",
            "range": "stddev: 0.00045807472360905944",
            "extra": "mean: 34.25027328571417 msec\nrounds: 7"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.8985448278895174,
            "unit": "iter/sec",
            "range": "stddev: 0.004149908943205425",
            "extra": "mean: 526.7191932000003 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 29.307917931541915,
            "unit": "iter/sec",
            "range": "stddev: 0.00035757762181228947",
            "extra": "mean: 34.12047223333374 msec\nrounds: 30"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 26.229543233148448,
            "unit": "iter/sec",
            "range": "stddev: 0.0003601899598716842",
            "extra": "mean: 38.12494907407374 msec\nrounds: 27"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 23.500063618098935,
            "unit": "iter/sec",
            "range": "stddev: 0.000990959194806741",
            "extra": "mean: 42.553076291667345 msec\nrounds: 24"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 108.93448697361741,
            "unit": "iter/sec",
            "range": "stddev: 0.0002603520067684724",
            "extra": "mean: 9.179829343137108 msec\nrounds: 102"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 30.697503896647547,
            "unit": "iter/sec",
            "range": "stddev: 0.0004021817817687387",
            "extra": "mean: 32.575938531250074 msec\nrounds: 32"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 49.813098663534205,
            "unit": "iter/sec",
            "range": "stddev: 0.0002096459882960457",
            "extra": "mean: 20.075041039999633 msec\nrounds: 50"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 87.66281619465764,
            "unit": "iter/sec",
            "range": "stddev: 0.0002337599648170319",
            "extra": "mean: 11.407345136841977 msec\nrounds: 95"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 106.33549399935194,
            "unit": "iter/sec",
            "range": "stddev: 0.0017354682702248358",
            "extra": "mean: 9.404197623853559 msec\nrounds: 109"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 45.85444711734543,
            "unit": "iter/sec",
            "range": "stddev: 0.00036199711474412726",
            "extra": "mean: 21.808135586956592 msec\nrounds: 46"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 38897.17530780564,
            "unit": "iter/sec",
            "range": "stddev: 0.00000191546552163474",
            "extra": "mean: 25.70880769841727 usec\nrounds: 18965"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 37317.942813139605,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021673516568083284",
            "extra": "mean: 26.796761145362527 usec\nrounds: 14109"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 46367.48038199326,
            "unit": "iter/sec",
            "range": "stddev: 0.000007082070070573605",
            "extra": "mean: 21.56683934002048 usec\nrounds: 17758"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 29780.59528843947,
            "unit": "iter/sec",
            "range": "stddev: 0.000009517594404737091",
            "extra": "mean: 33.57891238622051 usec\nrounds: 13297"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 77540.37514256571,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015199869725614852",
            "extra": "mean: 12.896507118535347 usec\nrounds: 26410"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 73764.35851067789,
            "unit": "iter/sec",
            "range": "stddev: 0.000001577752531828059",
            "extra": "mean: 13.556682660708603 usec\nrounds: 22175"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 31566.97731525285,
            "unit": "iter/sec",
            "range": "stddev: 0.000006650795360795423",
            "extra": "mean: 31.678674521580177 usec\nrounds: 14004"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 25960.918205549573,
            "unit": "iter/sec",
            "range": "stddev: 0.000007580865799144753",
            "extra": "mean: 38.5194387995966 usec\nrounds: 13129"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 5917.642673878323,
            "unit": "iter/sec",
            "range": "stddev: 0.000028755943346053133",
            "extra": "mean: 168.98620871689383 usec\nrounds: 3694"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1646.1600307430592,
            "unit": "iter/sec",
            "range": "stddev: 0.0005368091648501955",
            "extra": "mean: 607.4743532368542 usec\nrounds: 1591"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 8907.837642486265,
            "unit": "iter/sec",
            "range": "stddev: 0.0003593882720456787",
            "extra": "mean: 112.26068998277006 usec\nrounds: 10422"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 86.8863128762436,
            "unit": "iter/sec",
            "range": "stddev: 0.0018186625427229512",
            "extra": "mean: 11.509292625000082 msec\nrounds: 88"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 65.93865693775724,
            "unit": "iter/sec",
            "range": "stddev: 0.00016057877969036886",
            "extra": "mean: 15.165610681818245 msec\nrounds: 66"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 678.7837195584513,
            "unit": "iter/sec",
            "range": "stddev: 0.0006508520848661077",
            "extra": "mean: 1.4732233127961585 msec\nrounds: 633"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 261.56302815730584,
            "unit": "iter/sec",
            "range": "stddev: 0.003925518366574299",
            "extra": "mean: 3.8231702968303036 msec\nrounds: 347"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 94.17215563662319,
            "unit": "iter/sec",
            "range": "stddev: 0.00017854739715556805",
            "extra": "mean: 10.618850054347739 msec\nrounds: 92"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 811.5418654657194,
            "unit": "iter/sec",
            "range": "stddev: 0.0011879837741273827",
            "extra": "mean: 1.232222319702669 msec\nrounds: 807"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 1776.4779164443732,
            "unit": "iter/sec",
            "range": "stddev: 0.000023530036498463072",
            "extra": "mean: 562.9115851895888 usec\nrounds: 1661"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 15.978153101090689,
            "unit": "iter/sec",
            "range": "stddev: 0.00029241676153618794",
            "extra": "mean: 62.585456133333636 msec\nrounds: 15"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 77.45514252816432,
            "unit": "iter/sec",
            "range": "stddev: 0.00011068029615039237",
            "extra": "mean: 12.910698597402735 msec\nrounds: 77"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 10.200259397696668,
            "unit": "iter/sec",
            "range": "stddev: 0.0076605305837221865",
            "extra": "mean: 98.03672249999948 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 24.068513757111305,
            "unit": "iter/sec",
            "range": "stddev: 0.005353351645189147",
            "extra": "mean: 41.54805776923135 msec\nrounds: 26"
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
          "id": "f9785c1a1474d298490467157a9c89e86b8358b0",
          "message": "docs: record slicing in the HIR/VM subset\n\n- Update the supported subset, HIR/bytecode instructions and VM coverage in\n  the design note and OP 0004 progress.\n- Refresh the roadmap and CHANGELOG.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-21T16:42:01+08:00",
          "tree_id": "d4a1aedc987009c4f469a0538f12e4953b150def",
          "url": "https://github.com/fyabc/oort-lang.py/commit/f9785c1a1474d298490467157a9c89e86b8358b0"
        },
        "date": 1795250847960,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 18.291313576637112,
            "unit": "iter/sec",
            "range": "stddev: 0.0006117470774930507",
            "extra": "mean: 54.670759199999 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.355425610173391,
            "unit": "iter/sec",
            "range": "stddev: 0.009807459212124572",
            "extra": "mean: 737.7756421999997 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 20.934148871417328,
            "unit": "iter/sec",
            "range": "stddev: 0.0006319587314639445",
            "extra": "mean: 47.76883961904757 msec\nrounds: 21"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 18.452089790312428,
            "unit": "iter/sec",
            "range": "stddev: 0.002764514887487882",
            "extra": "mean: 54.194403526315604 msec\nrounds: 19"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 17.536888292627516,
            "unit": "iter/sec",
            "range": "stddev: 0.0005202686718465912",
            "extra": "mean: 57.02265894117593 msec\nrounds: 17"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 80.2065806037127,
            "unit": "iter/sec",
            "range": "stddev: 0.001991012104975966",
            "extra": "mean: 12.467804916666784 msec\nrounds: 84"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 21.251808642764093,
            "unit": "iter/sec",
            "range": "stddev: 0.000483159678697607",
            "extra": "mean: 47.054818571429415 msec\nrounds: 21"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 35.848805343832595,
            "unit": "iter/sec",
            "range": "stddev: 0.0013282769393281278",
            "extra": "mean: 27.894932352942114 msec\nrounds: 34"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 53.00258556241244,
            "unit": "iter/sec",
            "range": "stddev: 0.0029942631653367977",
            "extra": "mean: 18.867004116666426 msec\nrounds: 60"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 82.3718997668238,
            "unit": "iter/sec",
            "range": "stddev: 0.002256321339375222",
            "extra": "mean: 12.140062361445755 msec\nrounds: 83"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 32.395581829293334,
            "unit": "iter/sec",
            "range": "stddev: 0.000576662128329421",
            "extra": "mean: 30.868406848484547 msec\nrounds: 33"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 29515.421885015832,
            "unit": "iter/sec",
            "range": "stddev: 0.0000026118496444961197",
            "extra": "mean: 33.88059313181196 usec\nrounds: 15317"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 25379.068211628433,
            "unit": "iter/sec",
            "range": "stddev: 0.000004371362573369709",
            "extra": "mean: 39.40254983600265 usec\nrounds: 12802"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 35040.05430420821,
            "unit": "iter/sec",
            "range": "stddev: 0.0000030242600162903326",
            "extra": "mean: 28.53876855664298 usec\nrounds: 13122"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 22313.931888253723,
            "unit": "iter/sec",
            "range": "stddev: 0.000009607626304018785",
            "extra": "mean: 44.81505119796525 usec\nrounds: 10977"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 60688.006021794936,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017644470094811915",
            "extra": "mean: 16.477720484684717 usec\nrounds: 21870"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 56004.19668062798,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021601254652366223",
            "extra": "mean: 17.855804730181998 usec\nrounds: 18308"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 22841.782698377072,
            "unit": "iter/sec",
            "range": "stddev: 0.00000995584747631906",
            "extra": "mean: 43.779420074381974 usec\nrounds: 10222"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 19922.91836255781,
            "unit": "iter/sec",
            "range": "stddev: 0.000009573360600455674",
            "extra": "mean: 50.1934496644504 usec\nrounds: 9983"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 4388.672188632596,
            "unit": "iter/sec",
            "range": "stddev: 0.00003631364536093714",
            "extra": "mean: 227.8593517625147 usec\nrounds: 2695"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1284.85503283555,
            "unit": "iter/sec",
            "range": "stddev: 0.0009246674113994066",
            "extra": "mean: 778.2979203444434 usec\nrounds: 929"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 6711.415576208458,
            "unit": "iter/sec",
            "range": "stddev: 0.0005134161326345337",
            "extra": "mean: 148.99986279272235 usec\nrounds: 3287"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 68.90276612609111,
            "unit": "iter/sec",
            "range": "stddev: 0.00022098237972761537",
            "extra": "mean: 14.513205437500343 msec\nrounds: 64"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 48.32390017710391,
            "unit": "iter/sec",
            "range": "stddev: 0.00031542875956421483",
            "extra": "mean: 20.693693934783116 msec\nrounds: 46"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 537.9490036041482,
            "unit": "iter/sec",
            "range": "stddev: 0.000052597961129947567",
            "extra": "mean: 1.8589122636164481 msec\nrounds: 459"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 184.6754717530563,
            "unit": "iter/sec",
            "range": "stddev: 0.0050569142790074",
            "extra": "mean: 5.4149042669682546 msec\nrounds: 221"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 73.91900955919444,
            "unit": "iter/sec",
            "range": "stddev: 0.0027943036976987756",
            "extra": "mean: 13.528319791666021 msec\nrounds: 72"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 560.6403151236354,
            "unit": "iter/sec",
            "range": "stddev: 0.0017828039171506119",
            "extra": "mean: 1.7836747965216784 msec\nrounds: 575"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 1102.142831010418,
            "unit": "iter/sec",
            "range": "stddev: 0.000021219562356622625",
            "extra": "mean: 907.3234174950121 usec\nrounds: 1006"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 11.343412554320032,
            "unit": "iter/sec",
            "range": "stddev: 0.0010823586121982234",
            "extra": "mean: 88.15689239999998 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 57.23969747229136,
            "unit": "iter/sec",
            "range": "stddev: 0.00005653783410859202",
            "extra": "mean: 17.470392824561674 msec\nrounds: 57"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 8.260074882167723,
            "unit": "iter/sec",
            "range": "stddev: 0.009955111435046914",
            "extra": "mean: 121.06427777777797 msec\nrounds: 9"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 16.575934162393086,
            "unit": "iter/sec",
            "range": "stddev: 0.008451619449713677",
            "extra": "mean: 60.32842494444542 msec\nrounds: 18"
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
          "id": "02b263d907e916bf6780dbb5079ca35dacf34edf",
          "message": "docs: record attribute access in the HIR/VM subset\n\n- Update the supported subset, HIR/bytecode instructions and VM coverage in\n  the design note and OP 0004 progress.\n- Record the built-in attribute-assignment fix, refresh the roadmap and\n  CHANGELOG.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-21T16:51:44+08:00",
          "tree_id": "ee8713cd616e3a93eeb9145cfc48e4b47be7fb35",
          "url": "https://github.com/fyabc/oort-lang.py/commit/02b263d907e916bf6780dbb5079ca35dacf34edf"
        },
        "date": 1795251307554,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 27.552257303705368,
            "unit": "iter/sec",
            "range": "stddev: 0.0016588830774301449",
            "extra": "mean: 36.29466685713315 msec\nrounds: 7"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.892273869968035,
            "unit": "iter/sec",
            "range": "stddev: 0.02247180084742459",
            "extra": "mean: 345.74872400000345 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 47.300890138546336,
            "unit": "iter/sec",
            "range": "stddev: 0.00033651032719109",
            "extra": "mean: 21.1412511914883 msec\nrounds: 47"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 44.146437980690315,
            "unit": "iter/sec",
            "range": "stddev: 0.0004661289979414226",
            "extra": "mean: 22.651884177776715 msec\nrounds: 45"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 42.2426995585826,
            "unit": "iter/sec",
            "range": "stddev: 0.000485406852438933",
            "extra": "mean: 23.67272949999774 msec\nrounds: 42"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 169.1515966724651,
            "unit": "iter/sec",
            "range": "stddev: 0.0001227475296859597",
            "extra": "mean: 5.911856699386287 msec\nrounds: 163"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 51.67746979005008,
            "unit": "iter/sec",
            "range": "stddev: 0.000530068060418039",
            "extra": "mean: 19.350792599999522 msec\nrounds: 50"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 80.09495579417033,
            "unit": "iter/sec",
            "range": "stddev: 0.0001758843043868248",
            "extra": "mean: 12.485180746835303 msec\nrounds: 79"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 94.244041904045,
            "unit": "iter/sec",
            "range": "stddev: 0.000706899964608058",
            "extra": "mean: 10.61075034343449 msec\nrounds: 99"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 166.48854586292322,
            "unit": "iter/sec",
            "range": "stddev: 0.0014032545794714411",
            "extra": "mean: 6.006419209303087 msec\nrounds: 172"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 72.40644929954573,
            "unit": "iter/sec",
            "range": "stddev: 0.00024096506139272347",
            "extra": "mean: 13.810924436620233 msec\nrounds: 71"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 58788.70262497599,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014597596735199126",
            "extra": "mean: 17.010070903914738 usec\nrounds: 26684"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 56410.498385456536,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010441490599509506",
            "extra": "mean: 17.72719668539243 usec\nrounds: 24679"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 91607.07391952524,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010308650116690008",
            "extra": "mean: 10.916187552049502 usec\nrounds: 22751"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 51479.79347397122,
            "unit": "iter/sec",
            "range": "stddev: 0.000006251399767586079",
            "extra": "mean: 19.425097354083434 usec\nrounds: 17914"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 119619.11511374214,
            "unit": "iter/sec",
            "range": "stddev: 8.566020569730517e-7",
            "extra": "mean: 8.359867894434185 usec\nrounds: 34480"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 112011.71452805045,
            "unit": "iter/sec",
            "range": "stddev: 9.381658216240628e-7",
            "extra": "mean: 8.927637651234914 usec\nrounds: 27537"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 55805.52718888517,
            "unit": "iter/sec",
            "range": "stddev: 0.000003817048959116106",
            "extra": "mean: 17.91937197574169 usec\nrounds: 13888"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 43778.6559704882,
            "unit": "iter/sec",
            "range": "stddev: 0.0000052481076127191",
            "extra": "mean: 22.84218137427777 usec\nrounds: 14539"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 8876.482963133432,
            "unit": "iter/sec",
            "range": "stddev: 0.000020139256287291206",
            "extra": "mean: 112.65723194121877 usec\nrounds: 4070"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 2440.9893864953415,
            "unit": "iter/sec",
            "range": "stddev: 0.0000984375823701327",
            "extra": "mean: 409.66995003438063 usec\nrounds: 1461"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 11967.083478822227,
            "unit": "iter/sec",
            "range": "stddev: 0.00033670479777346454",
            "extra": "mean: 83.56254903458046 usec\nrounds: 14398"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 123.75417513421469,
            "unit": "iter/sec",
            "range": "stddev: 0.0017757707845302115",
            "extra": "mean: 8.080535455999552 msec\nrounds: 125"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 93.92786121093165,
            "unit": "iter/sec",
            "range": "stddev: 0.00007954632342515915",
            "extra": "mean: 10.64646833333427 msec\nrounds: 93"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 939.0327519000253,
            "unit": "iter/sec",
            "range": "stddev: 0.00013247558142679905",
            "extra": "mean: 1.0649255821765689 msec\nrounds: 864"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 311.24759370149053,
            "unit": "iter/sec",
            "range": "stddev: 0.0034830163936284604",
            "extra": "mean: 3.212876244624317 msec\nrounds: 372"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 126.31180641696022,
            "unit": "iter/sec",
            "range": "stddev: 0.0022454835347443147",
            "extra": "mean: 7.916916307086614 msec\nrounds: 127"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 1033.3308350410787,
            "unit": "iter/sec",
            "range": "stddev: 0.0010182888482038947",
            "extra": "mean: 967.7442752013167 usec\nrounds: 992"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 1957.4037360348686,
            "unit": "iter/sec",
            "range": "stddev: 0.000020457998648506985",
            "extra": "mean: 510.8808068516868 usec\nrounds: 1693"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 21.109530355202068,
            "unit": "iter/sec",
            "range": "stddev: 0.0006792275444939495",
            "extra": "mean: 47.371968166670634 msec\nrounds: 18"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 86.70832322211946,
            "unit": "iter/sec",
            "range": "stddev: 0.00010951718245354916",
            "extra": "mean: 11.532918211765143 msec\nrounds: 85"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 13.83287808094846,
            "unit": "iter/sec",
            "range": "stddev: 0.00712977817629134",
            "extra": "mean: 72.29153572728043 msec\nrounds: 11"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 26.566522137352262,
            "unit": "iter/sec",
            "range": "stddev: 0.005636677852048875",
            "extra": "mean: 37.64135910714523 msec\nrounds: 28"
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
          "id": "90ed153f0a7c3c280c4dfe7c9b479740c8b1aad3",
          "message": "docs: record lambda and closure support in the HIR/VM subset\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-21T17:09:24+08:00",
          "tree_id": "a45f5be238edcd049e7bac5ffb1e768e21021037",
          "url": "https://github.com/fyabc/oort-lang.py/commit/90ed153f0a7c3c280c4dfe7c9b479740c8b1aad3"
        },
        "date": 1795252420630,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 25.084235056187865,
            "unit": "iter/sec",
            "range": "stddev: 0.0002956204089022133",
            "extra": "mean: 39.8656765000022 msec\nrounds: 6"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.132221463195903,
            "unit": "iter/sec",
            "range": "stddev: 0.0021299874582392155",
            "extra": "mean: 468.994434800004 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 32.655619292432455,
            "unit": "iter/sec",
            "range": "stddev: 0.0002411489964985727",
            "extra": "mean: 30.62260099999812 msec\nrounds: 33"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 30.085555614382137,
            "unit": "iter/sec",
            "range": "stddev: 0.0017472273668260726",
            "extra": "mean: 33.23854187096877 msec\nrounds: 31"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 29.689957776456055,
            "unit": "iter/sec",
            "range": "stddev: 0.00024681720168050203",
            "extra": "mean: 33.68142210000021 msec\nrounds: 30"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 115.76965749693753,
            "unit": "iter/sec",
            "range": "stddev: 0.00011376332435466842",
            "extra": "mean: 8.637841914894265 msec\nrounds: 47"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 35.58565293428246,
            "unit": "iter/sec",
            "range": "stddev: 0.00013083650937376843",
            "extra": "mean: 28.101212638889688 msec\nrounds: 36"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 56.35469345380287,
            "unit": "iter/sec",
            "range": "stddev: 0.00016711999156664387",
            "extra": "mean: 17.744750946427498 msec\nrounds: 56"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 84.32756217526266,
            "unit": "iter/sec",
            "range": "stddev: 0.00016379541033990184",
            "extra": "mean: 11.858519020408114 msec\nrounds: 98"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 116.3304889351918,
            "unit": "iter/sec",
            "range": "stddev: 0.00009314511733137037",
            "extra": "mean: 8.59619871929795 msec\nrounds: 114"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 50.74070096290467,
            "unit": "iter/sec",
            "range": "stddev: 0.00019806517001049462",
            "extra": "mean: 19.7080446470591 msec\nrounds: 51"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 40883.766826177096,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018708021766275682",
            "extra": "mean: 24.45958573855575 usec\nrounds: 18259"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 39508.370010010694,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018099045164945079",
            "extra": "mean: 25.311092301368507 usec\nrounds: 17237"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 62548.28965713756,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013015669274270325",
            "extra": "mean: 15.987647391824202 usec\nrounds: 16429"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 40022.30397989525,
            "unit": "iter/sec",
            "range": "stddev: 0.000007096390408266343",
            "extra": "mean: 24.986067781163687 usec\nrounds: 13160"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 84351.96652635146,
            "unit": "iter/sec",
            "range": "stddev: 0.000001186985513459752",
            "extra": "mean: 11.855088164276538 usec\nrounds: 24840"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 78392.86292418679,
            "unit": "iter/sec",
            "range": "stddev: 0.000001199915213213559",
            "extra": "mean: 12.756263296150992 usec\nrounds: 21698"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 40013.83311282967,
            "unit": "iter/sec",
            "range": "stddev: 0.000006068571205538473",
            "extra": "mean: 24.991357293369852 usec\nrounds: 12340"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 35063.69849895628,
            "unit": "iter/sec",
            "range": "stddev: 0.000006747602788022616",
            "extra": "mean: 28.519524260390458 usec\nrounds: 11830"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 7353.138807022206,
            "unit": "iter/sec",
            "range": "stddev: 0.00003229832512923952",
            "extra": "mean: 135.9963447235629 usec\nrounds: 3307"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1788.657955647964,
            "unit": "iter/sec",
            "range": "stddev: 0.0008487471171337865",
            "extra": "mean: 559.0783843508734 usec\nrounds: 1163"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 9085.463493806676,
            "unit": "iter/sec",
            "range": "stddev: 0.00038656975959085795",
            "extra": "mean: 110.06593121877316 usec\nrounds: 11224"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 96.21179695843682,
            "unit": "iter/sec",
            "range": "stddev: 0.0030169071707604176",
            "extra": "mean: 10.393735816326107 msec\nrounds: 98"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 73.32196881921965,
            "unit": "iter/sec",
            "range": "stddev: 0.0002284570298202559",
            "extra": "mean: 13.63847719999948 msec\nrounds: 30"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 758.9753479121989,
            "unit": "iter/sec",
            "range": "stddev: 0.00013825792127443895",
            "extra": "mean: 1.3175658507892454 msec\nrounds: 697"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 226.12316178221934,
            "unit": "iter/sec",
            "range": "stddev: 0.004651068285902976",
            "extra": "mean: 4.4223687309091595 msec\nrounds: 275"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 101.581757834792,
            "unit": "iter/sec",
            "range": "stddev: 0.002241927651320547",
            "extra": "mean: 9.844287215686453 msec\nrounds: 102"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 727.8319929722214,
            "unit": "iter/sec",
            "range": "stddev: 0.0017242318236896355",
            "extra": "mean: 1.3739434507630475 msec\nrounds: 721"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 1652.5231404335796,
            "unit": "iter/sec",
            "range": "stddev: 0.0000314519655061389",
            "extra": "mean: 605.1352477506763 usec\nrounds: 1445"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 18.48279021542617,
            "unit": "iter/sec",
            "range": "stddev: 0.0005255033281267653",
            "extra": "mean: 54.10438512500004 msec\nrounds: 16"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 31.651533626881463,
            "unit": "iter/sec",
            "range": "stddev: 0.00030819993293977084",
            "extra": "mean: 31.594045703703465 msec\nrounds: 27"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 10.982061546498537,
            "unit": "iter/sec",
            "range": "stddev: 0.009482695763196153",
            "extra": "mean: 91.0575847499994 msec\nrounds: 12"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 20.498871456062872,
            "unit": "iter/sec",
            "range": "stddev: 0.00784707334028402",
            "extra": "mean: 48.783173363635775 msec\nrounds: 22"
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
          "id": "5e054f92ca8a3e47a9eac1378e0067b56af6a520",
          "message": "docs: record class and method support in the HIR/VM subset\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-21T19:18:12+08:00",
          "tree_id": "4735182eb691d554d75197deef56077e44304241",
          "url": "https://github.com/fyabc/oort-lang.py/commit/5e054f92ca8a3e47a9eac1378e0067b56af6a520"
        },
        "date": 1795259941054,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 17.988636707709738,
            "unit": "iter/sec",
            "range": "stddev: 0.001063772010013661",
            "extra": "mean: 55.590649600000575 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.3475881248300656,
            "unit": "iter/sec",
            "range": "stddev: 0.007460362542739439",
            "extra": "mean: 742.0664976000012 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 20.5271190171845,
            "unit": "iter/sec",
            "range": "stddev: 0.0014728690732674977",
            "extra": "mean: 48.71604238095171 msec\nrounds: 21"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 18.578720054127125,
            "unit": "iter/sec",
            "range": "stddev: 0.0006174874075459923",
            "extra": "mean: 53.825021157894966 msec\nrounds: 19"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 17.484780807237197,
            "unit": "iter/sec",
            "range": "stddev: 0.0007362612737496261",
            "extra": "mean: 57.19259572222294 msec\nrounds: 18"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 82.83245298211054,
            "unit": "iter/sec",
            "range": "stddev: 0.0017649224913644191",
            "extra": "mean: 12.072562914634094 msec\nrounds: 82"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 21.638208776259535,
            "unit": "iter/sec",
            "range": "stddev: 0.0006188703561504126",
            "extra": "mean: 46.21454623809503 msec\nrounds: 21"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 35.79512980454803,
            "unit": "iter/sec",
            "range": "stddev: 0.0002644875184815146",
            "extra": "mean: 27.93676138235271 msec\nrounds: 34"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 54.89999141293314,
            "unit": "iter/sec",
            "range": "stddev: 0.00022438274047538348",
            "extra": "mean: 18.214939096774135 msec\nrounds: 62"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 83.07253320398411,
            "unit": "iter/sec",
            "range": "stddev: 0.0019489473817233137",
            "extra": "mean: 12.037673120482628 msec\nrounds: 83"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 31.809002234529597,
            "unit": "iter/sec",
            "range": "stddev: 0.0003481356572870185",
            "extra": "mean: 31.437641225805912 msec\nrounds: 31"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 29920.22801057612,
            "unit": "iter/sec",
            "range": "stddev: 0.0000029323198593334057",
            "extra": "mean: 33.422205193306766 usec\nrounds: 15366"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 26329.63706704031,
            "unit": "iter/sec",
            "range": "stddev: 0.000003227138746232975",
            "extra": "mean: 37.980014591686476 usec\nrounds: 13912"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 35880.69466826282,
            "unit": "iter/sec",
            "range": "stddev: 0.0000027989891740426355",
            "extra": "mean: 27.870140454234843 usec\nrounds: 13912"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 22488.917389756585,
            "unit": "iter/sec",
            "range": "stddev: 0.000010932909401161319",
            "extra": "mean: 44.4663468084723 usec\nrounds: 11280"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 61313.69897069301,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018689175311310895",
            "extra": "mean: 16.309568934635383 usec\nrounds: 22340"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 55668.888764263844,
            "unit": "iter/sec",
            "range": "stddev: 0.000001920238401371524",
            "extra": "mean: 17.963354796511428 usec\nrounds: 19118"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 22672.54986494832,
            "unit": "iter/sec",
            "range": "stddev: 0.000009928512817217097",
            "extra": "mean: 44.10619916844891 usec\nrounds: 9861"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 20147.79235653779,
            "unit": "iter/sec",
            "range": "stddev: 0.000009299772325457237",
            "extra": "mean: 49.63322940319604 usec\nrounds: 10305"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 4319.629722264621,
            "unit": "iter/sec",
            "range": "stddev: 0.0000366808003130103",
            "extra": "mean: 231.5013240245364 usec\nrounds: 2435"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1293.6227759466924,
            "unit": "iter/sec",
            "range": "stddev: 0.0007509112119036994",
            "extra": "mean: 773.0228769883748 usec\nrounds: 943"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 6674.149097272882,
            "unit": "iter/sec",
            "range": "stddev: 0.0004350504831462767",
            "extra": "mean: 149.83183405486238 usec\nrounds: 8316"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 64.74550927061046,
            "unit": "iter/sec",
            "range": "stddev: 0.0038459141425087745",
            "extra": "mean: 15.445086636362653 msec\nrounds: 66"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 49.03826130625069,
            "unit": "iter/sec",
            "range": "stddev: 0.0002966164914959399",
            "extra": "mean: 20.392240127659957 msec\nrounds: 47"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 519.9489013444107,
            "unit": "iter/sec",
            "range": "stddev: 0.000267632500343316",
            "extra": "mean: 1.9232659159666279 msec\nrounds: 476"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 199.73844535918343,
            "unit": "iter/sec",
            "range": "stddev: 0.003905539766286446",
            "extra": "mean: 5.006547428572056 msec\nrounds: 35"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 74.7577692698646,
            "unit": "iter/sec",
            "range": "stddev: 0.002496358633010606",
            "extra": "mean: 13.376536108108665 msec\nrounds: 74"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 571.4215449139244,
            "unit": "iter/sec",
            "range": "stddev: 0.0015242963487595786",
            "extra": "mean: 1.7500215189657122 msec\nrounds: 580"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 1135.0547012662912,
            "unit": "iter/sec",
            "range": "stddev: 0.000014472875091054732",
            "extra": "mean: 881.014808259354 usec\nrounds: 1017"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 11.234641297423787,
            "unit": "iter/sec",
            "range": "stddev: 0.0010369628108139932",
            "extra": "mean: 89.01040749999822 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 13.967965447732903,
            "unit": "iter/sec",
            "range": "stddev: 0.007910965546024216",
            "extra": "mean: 71.59238786363886 msec\nrounds: 22"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 8.26962844205664,
            "unit": "iter/sec",
            "range": "stddev: 0.007194583841969008",
            "extra": "mean: 120.92441722222071 msec\nrounds: 9"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 15.164714427045507,
            "unit": "iter/sec",
            "range": "stddev: 0.00691781164515694",
            "extra": "mean: 65.9425539999982 msec\nrounds: 12"
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
          "id": "7ae89f7aed0bdd4b713790047edb71753ec6ae16",
          "message": "docs: record OP 0019 and parameter binding in the HIR/VM\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-21T21:51:56+08:00",
          "tree_id": "05444e033710beb6f75c3fbc6bf0d55fc5ea64ae",
          "url": "https://github.com/fyabc/oort-lang.py/commit/7ae89f7aed0bdd4b713790047edb71753ec6ae16"
        },
        "date": 1795269166930,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 21.55705114544083,
            "unit": "iter/sec",
            "range": "stddev: 0.0005250754946601175",
            "extra": "mean: 46.38853399999903 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.2570618481984244,
            "unit": "iter/sec",
            "range": "stddev: 0.0042100437006439085",
            "extra": "mean: 795.5058070000007 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 21.095412935069593,
            "unit": "iter/sec",
            "range": "stddev: 0.00037662564558870154",
            "extra": "mean: 47.40367031818431 msec\nrounds: 22"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 19.065880983954617,
            "unit": "iter/sec",
            "range": "stddev: 0.000490365878977999",
            "extra": "mean: 52.449713750000626 msec\nrounds: 20"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 16.85814367910722,
            "unit": "iter/sec",
            "range": "stddev: 0.00054907216752203",
            "extra": "mean: 59.31851211111273 msec\nrounds: 18"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 85.7818757473457,
            "unit": "iter/sec",
            "range": "stddev: 0.0019389795356801627",
            "extra": "mean: 11.657474160920788 msec\nrounds: 87"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 22.514987916651386,
            "unit": "iter/sec",
            "range": "stddev: 0.00042863186555133233",
            "extra": "mean: 44.41485839130436 msec\nrounds: 23"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 34.60690269343753,
            "unit": "iter/sec",
            "range": "stddev: 0.00040585623713123973",
            "extra": "mean: 28.8959693636388 msec\nrounds: 33"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 59.67351821941675,
            "unit": "iter/sec",
            "range": "stddev: 0.00019342585496323877",
            "extra": "mean: 16.757852223880057 msec\nrounds: 67"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 87.87354048490488,
            "unit": "iter/sec",
            "range": "stddev: 0.0025434038886108464",
            "extra": "mean: 11.379989863635714 msec\nrounds: 88"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 31.484954281347196,
            "unit": "iter/sec",
            "range": "stddev: 0.000663383852245327",
            "extra": "mean: 31.761202225802037 msec\nrounds: 31"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 29513.55064476772,
            "unit": "iter/sec",
            "range": "stddev: 0.0000028602224169539414",
            "extra": "mean: 33.88274125455942 usec\nrounds: 13550"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 29311.42924198344,
            "unit": "iter/sec",
            "range": "stddev: 0.0000031336526448073396",
            "extra": "mean: 34.1163848321554 usec\nrounds: 12065"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 31712.71612821019,
            "unit": "iter/sec",
            "range": "stddev: 0.0000031421379822989987",
            "extra": "mean: 31.533092150074317 usec\nrounds: 8497"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 20145.996489279205,
            "unit": "iter/sec",
            "range": "stddev: 0.000014476791170353197",
            "extra": "mean: 49.637653840163985 usec\nrounds: 6341"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 60900.065167092085,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018262380978474154",
            "extra": "mean: 16.420343677076378 usec\nrounds: 18433"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 55518.96727826438,
            "unit": "iter/sec",
            "range": "stddev: 0.000002273106965597565",
            "extra": "mean: 18.011862414297806 usec\nrounds: 15772"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 19759.31252005654,
            "unit": "iter/sec",
            "range": "stddev: 0.000007720195980916793",
            "extra": "mean: 50.60904821384639 usec\nrounds: 6803"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 18097.979826312778,
            "unit": "iter/sec",
            "range": "stddev: 0.000008220440925265027",
            "extra": "mean: 55.25478587096738 usec\nrounds: 6837"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 4912.9274244670605,
            "unit": "iter/sec",
            "range": "stddev: 0.00004535676154187421",
            "extra": "mean: 203.54463105232557 usec\nrounds: 2499"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1354.0524657631838,
            "unit": "iter/sec",
            "range": "stddev: 0.0009064961625264491",
            "extra": "mean: 738.5238203723299 usec\nrounds: 913"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 7422.948104470364,
            "unit": "iter/sec",
            "range": "stddev: 0.0005917254654494147",
            "extra": "mean: 134.71736376518172 usec\nrounds: 3527"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 50.23543625898734,
            "unit": "iter/sec",
            "range": "stddev: 0.0003192652069821876",
            "extra": "mean: 19.90626686000155 msec\nrounds: 50"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 38.75440700583837,
            "unit": "iter/sec",
            "range": "stddev: 0.0044387706971894475",
            "extra": "mean: 25.80351699999821 msec\nrounds: 41"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 435.6581942431979,
            "unit": "iter/sec",
            "range": "stddev: 0.00005676361032978024",
            "extra": "mean: 2.2953774615375853 msec\nrounds: 403"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 198.47650598006487,
            "unit": "iter/sec",
            "range": "stddev: 0.006464244922439912",
            "extra": "mean: 5.0383797067671106 msec\nrounds: 266"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 52.770481965473294,
            "unit": "iter/sec",
            "range": "stddev: 0.0003698548642387036",
            "extra": "mean: 18.949988000001227 msec\nrounds: 54"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 680.9176662519908,
            "unit": "iter/sec",
            "range": "stddev: 0.0017640325737178805",
            "extra": "mean: 1.468606337539089 msec\nrounds: 634"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 1468.7164169810467,
            "unit": "iter/sec",
            "range": "stddev: 0.000029002486364431017",
            "extra": "mean: 680.8666318685977 usec\nrounds: 1274"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 9.848353292254988,
            "unit": "iter/sec",
            "range": "stddev: 0.000503434806462642",
            "extra": "mean: 101.53981790909423 msec\nrounds: 11"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 27.885270849355003,
            "unit": "iter/sec",
            "range": "stddev: 0.00025735858375393615",
            "extra": "mean: 35.86122600000245 msec\nrounds: 23"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 8.746966038293483,
            "unit": "iter/sec",
            "range": "stddev: 0.0008529079741382412",
            "extra": "mean: 114.32535528571667 msec\nrounds: 7"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 16.016805800772147,
            "unit": "iter/sec",
            "range": "stddev: 0.0091990629897943",
            "extra": "mean: 62.43442122222594 msec\nrounds: 18"
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
          "id": "36f2ea582d799ba62d3c01fea048974b663a001c",
          "message": "docs: consolidate benchmark reporting and translate English docs\n\nAdd a JSON-driven report generator with a checked-in canonical snapshot,\nhistory metadata and shared memory limits. Point design, proposal and\nroadmap docs at the single results file instead of duplicating numbers.\nTranslate the remaining English project docs and templates to Chinese.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-21T22:37:18+08:00",
          "tree_id": "9fcfb17ff64b534adcdc0d3ce373643d68209631",
          "url": "https://github.com/fyabc/oort-lang.py/commit/36f2ea582d799ba62d3c01fea048974b663a001c"
        },
        "date": 1795271888488,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 40.08958811346834,
            "unit": "iter/sec",
            "range": "stddev: 0.00020438399349157114",
            "extra": "mean: 24.94413255555609 msec\nrounds: 9"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.1338830880801667,
            "unit": "iter/sec",
            "range": "stddev: 0.005175304398292777",
            "extra": "mean: 468.62923540000025 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 30.719764904295552,
            "unit": "iter/sec",
            "range": "stddev: 0.0005026720002669042",
            "extra": "mean: 32.55233245161228 msec\nrounds: 31"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 27.710486874026117,
            "unit": "iter/sec",
            "range": "stddev: 0.0003722773678973873",
            "extra": "mean: 36.087420785714535 msec\nrounds: 28"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 26.088110901742425,
            "unit": "iter/sec",
            "range": "stddev: 0.0002928187729845172",
            "extra": "mean: 38.331637111110645 msec\nrounds: 27"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 112.1966537178184,
            "unit": "iter/sec",
            "range": "stddev: 0.00028765889132504496",
            "extra": "mean: 8.912921792793057 msec\nrounds: 111"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 33.04586938509228,
            "unit": "iter/sec",
            "range": "stddev: 0.00031490083830544455",
            "extra": "mean: 30.2609681212116 msec\nrounds: 33"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 53.42805995296764,
            "unit": "iter/sec",
            "range": "stddev: 0.00022783181648962386",
            "extra": "mean: 18.71675671698155 msec\nrounds: 53"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 155.76369760160674,
            "unit": "iter/sec",
            "range": "stddev: 0.00025691150187563206",
            "extra": "mean: 6.419981134228574 msec\nrounds: 149"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 110.13636013937726,
            "unit": "iter/sec",
            "range": "stddev: 0.0019360635410079123",
            "extra": "mean: 9.079653610619625 msec\nrounds: 113"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 47.10615690425044,
            "unit": "iter/sec",
            "range": "stddev: 0.0002681151373340729",
            "extra": "mean: 21.228647499999493 msec\nrounds: 48"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 38977.99497831399,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021578338910220586",
            "extra": "mean: 25.6555012785128 usec\nrounds: 17208"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 37290.882737067586,
            "unit": "iter/sec",
            "range": "stddev: 0.000002434765105521725",
            "extra": "mean: 26.816206177012482 usec\nrounds: 14376"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 56347.581673274755,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019438555953560267",
            "extra": "mean: 17.746990559388863 usec\nrounds: 11334"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 32849.65856864699,
            "unit": "iter/sec",
            "range": "stddev: 0.000009448715705286126",
            "extra": "mean: 30.441716704916967 usec\nrounds: 9153"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 81851.18636097903,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013815840296248482",
            "extra": "mean: 12.217293902006661 usec\nrounds: 22089"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 76145.22473222633,
            "unit": "iter/sec",
            "range": "stddev: 0.00000564790443698606",
            "extra": "mean: 13.132799903298178 usec\nrounds: 14488"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 35249.66047311547,
            "unit": "iter/sec",
            "range": "stddev: 0.000006339859886263584",
            "extra": "mean: 28.3690675762023 usec\nrounds: 9308"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 29791.76619077357,
            "unit": "iter/sec",
            "range": "stddev: 0.000006690574117340466",
            "extra": "mean: 33.566321432453286 usec\nrounds: 9215"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 6398.322475273264,
            "unit": "iter/sec",
            "range": "stddev: 0.00042070999969986246",
            "extra": "mean: 156.29096593123674 usec\nrounds: 3082"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1900.9215767419919,
            "unit": "iter/sec",
            "range": "stddev: 0.00012965236655189085",
            "extra": "mean: 526.0606288208427 usec\nrounds: 1145"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 9621.99940048757,
            "unit": "iter/sec",
            "range": "stddev: 0.0005003820186368338",
            "extra": "mean: 103.92850366934418 usec\nrounds: 11855"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 93.75994238782702,
            "unit": "iter/sec",
            "range": "stddev: 0.0029711324481736462",
            "extra": "mean: 10.665535563829776 msec\nrounds: 94"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 69.75185193366178,
            "unit": "iter/sec",
            "range": "stddev: 0.0029765833363843072",
            "extra": "mean: 14.336536913042256 msec\nrounds: 69"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 753.6271430366822,
            "unit": "iter/sec",
            "range": "stddev: 0.0000355044264495031",
            "extra": "mean: 1.326916113942735 msec\nrounds: 667"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 246.25243240012713,
            "unit": "iter/sec",
            "range": "stddev: 0.00573058464442698",
            "extra": "mean: 4.06087359322053 msec\nrounds: 354"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 100.08621085909812,
            "unit": "iter/sec",
            "range": "stddev: 0.002496565155864871",
            "extra": "mean: 9.991386340000474 msec\nrounds: 100"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 868.6602121229676,
            "unit": "iter/sec",
            "range": "stddev: 0.0018107195957887054",
            "extra": "mean: 1.1511981164142924 msec\nrounds: 859"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 1946.66489931158,
            "unit": "iter/sec",
            "range": "stddev: 0.00001893802990719675",
            "extra": "mean: 513.6990965181736 usec\nrounds: 1637"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 21.87638133396584,
            "unit": "iter/sec",
            "range": "stddev: 0.0002200563546606672",
            "extra": "mean: 45.71139919047645 msec\nrounds: 21"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 59.641698052931275,
            "unit": "iter/sec",
            "range": "stddev: 0.00017344837439605413",
            "extra": "mean: 16.76679290909042 msec\nrounds: 55"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 11.020986813327845,
            "unit": "iter/sec",
            "range": "stddev: 0.007334060420330957",
            "extra": "mean: 90.73597645454807 msec\nrounds: 11"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 21.965658096438535,
            "unit": "iter/sec",
            "range": "stddev: 0.005688738494948671",
            "extra": "mean: 45.5256107333355 msec\nrounds: 15"
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
          "id": "1b199eb727de475c45936ea2c90ec41788250bdd",
          "message": "feat: add multi-variable for and Oort VM reference results\n\n- lower multi-variable `for` to a new UNPACK instruction and opcode, with\n  tuple/list length checks matching the interpreter\n- register `oort-vm` in the manual cross-language suite and render it as\n  its own row in the generated RESULTS report\n- document the VM-vs-tree-walker ratio semantics and update roadmap/HIR docs\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-21T23:01:28+08:00",
          "tree_id": "f3a555c6eeff2e51fc353f1bf0c1d450a14aae7b",
          "url": "https://github.com/fyabc/oort-lang.py/commit/1b199eb727de475c45936ea2c90ec41788250bdd"
        },
        "date": 1795273365728,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 25.521765050561523,
            "unit": "iter/sec",
            "range": "stddev: 0.000428720839349507",
            "extra": "mean: 39.18224299999965 msec\nrounds: 6"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.8989140654308814,
            "unit": "iter/sec",
            "range": "stddev: 0.008755921173031858",
            "extra": "mean: 526.6167743999994 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 29.0904862668619,
            "unit": "iter/sec",
            "range": "stddev: 0.0010776292671990204",
            "extra": "mean: 34.37549963333334 msec\nrounds: 30"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 26.064581072654963,
            "unit": "iter/sec",
            "range": "stddev: 0.0005512582285223288",
            "extra": "mean: 38.36624103846143 msec\nrounds: 26"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 24.6309645052983,
            "unit": "iter/sec",
            "range": "stddev: 0.000706961610601331",
            "extra": "mean: 40.59930336000008 msec\nrounds: 25"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 106.19639477804063,
            "unit": "iter/sec",
            "range": "stddev: 0.00023678125409256004",
            "extra": "mean: 9.416515523809297 msec\nrounds: 105"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 31.424663634075383,
            "unit": "iter/sec",
            "range": "stddev: 0.0005971619140567995",
            "extra": "mean: 31.822138548386828 msec\nrounds: 31"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 50.35163651080399,
            "unit": "iter/sec",
            "range": "stddev: 0.00029895852606425953",
            "extra": "mean: 19.860327673469545 msec\nrounds: 49"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 93.86932835024452,
            "unit": "iter/sec",
            "range": "stddev: 0.00013833433673818589",
            "extra": "mean: 10.653107011363794 msec\nrounds: 88"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 104.21074584787267,
            "unit": "iter/sec",
            "range": "stddev: 0.0022104027462403406",
            "extra": "mean: 9.595939380952178 msec\nrounds: 105"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 45.6422831376807,
            "unit": "iter/sec",
            "range": "stddev: 0.000494901573515518",
            "extra": "mean: 21.90950871111078 msec\nrounds: 45"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 36892.62553308796,
            "unit": "iter/sec",
            "range": "stddev: 0.0000033515504828677615",
            "extra": "mean: 27.105688075876525 usec\nrounds: 14869"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 35574.592509580856,
            "unit": "iter/sec",
            "range": "stddev: 0.0000029382892346884256",
            "extra": "mean: 28.109949530150843 usec\nrounds: 9471"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 53525.61673052991,
            "unit": "iter/sec",
            "range": "stddev: 0.0000023322531211107794",
            "extra": "mean: 18.682643210528777 usec\nrounds: 9905"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 30808.05625661589,
            "unit": "iter/sec",
            "range": "stddev: 0.000009710110337892892",
            "extra": "mean: 32.459042260585804 usec\nrounds: 7998"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 75591.96427855831,
            "unit": "iter/sec",
            "range": "stddev: 0.0000018858414692682538",
            "extra": "mean: 13.22891936390189 usec\nrounds: 19557"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 72419.1989393056,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017882086348229426",
            "extra": "mean: 13.80849297764393 usec\nrounds: 11321"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 32636.957711394272,
            "unit": "iter/sec",
            "range": "stddev: 0.000007497024937393346",
            "extra": "mean: 30.6401107861496 usec\nrounds: 8548"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 26008.843592271533,
            "unit": "iter/sec",
            "range": "stddev: 0.000010305231449685596",
            "extra": "mean: 38.44846067270548 usec\nrounds: 7730"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 6267.100062502963,
            "unit": "iter/sec",
            "range": "stddev: 0.000026706032995419278",
            "extra": "mean: 159.56343285200694 usec\nrounds: 2770"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1683.6281713185097,
            "unit": "iter/sec",
            "range": "stddev: 0.000827584313738773",
            "extra": "mean: 593.9553738975894 usec\nrounds: 1134"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 8705.363403681096,
            "unit": "iter/sec",
            "range": "stddev: 0.0005837425166189454",
            "extra": "mean: 114.87171225696864 usec\nrounds: 10492"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 86.2668501763512,
            "unit": "iter/sec",
            "range": "stddev: 0.003071621660985837",
            "extra": "mean: 11.591938246913477 msec\nrounds: 81"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 66.7173661089016,
            "unit": "iter/sec",
            "range": "stddev: 0.00028161826377312154",
            "extra": "mean: 14.988601294117595 msec\nrounds: 68"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 690.9033385458315,
            "unit": "iter/sec",
            "range": "stddev: 0.00004155449269856965",
            "extra": "mean: 1.447380471636937 msec\nrounds: 617"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 214.8798586573324,
            "unit": "iter/sec",
            "range": "stddev: 0.006967461622676883",
            "extra": "mean: 4.65376329940115 msec\nrounds: 334"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 92.77882518026537,
            "unit": "iter/sec",
            "range": "stddev: 0.0003175935175697464",
            "extra": "mean: 10.778321433333973 msec\nrounds: 90"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 802.8755455650103,
            "unit": "iter/sec",
            "range": "stddev: 0.0019405264333959384",
            "extra": "mean: 1.2455230521391292 msec\nrounds: 748"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 1811.4071356279737,
            "unit": "iter/sec",
            "range": "stddev: 0.000024069692550265314",
            "extra": "mean: 552.0570060321214 usec\nrounds: 1492"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 16.729853056159094,
            "unit": "iter/sec",
            "range": "stddev: 0.0013340889498247358",
            "extra": "mean: 59.7733881249991 msec\nrounds: 16"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 48.067912707990125,
            "unit": "iter/sec",
            "range": "stddev: 0.0002520034391671153",
            "extra": "mean: 20.803898976744506 msec\nrounds: 43"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 10.07920571548709,
            "unit": "iter/sec",
            "range": "stddev: 0.011229064231807756",
            "extra": "mean: 99.21416709091088 msec\nrounds: 11"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 19.15941889160641,
            "unit": "iter/sec",
            "range": "stddev: 0.008242614007549382",
            "extra": "mean: 52.19364979999952 msec\nrounds: 20"
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
          "id": "fa641ab0e9c801e94765c628c2400fec86d7ef42",
          "message": "feat: add class methods, operators and augmented assignment to VM\n\n- lower class methods into ClassSpec and bind them on the metaclass\n- lower operator methods into the type operator table, including\n  user-defined `\"[]\"` / `\"[]=\"` dispatch shared with the interpreter\n- lower augmented assignment for names, attributes and items\n- rename repository references from oort-lang.py to oort-lang\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-21T23:32:10+08:00",
          "tree_id": "7fef285e1c24f0e2aaedbc8a13bac1d2381a08a0",
          "url": "https://github.com/fyabc/oort-lang/commit/fa641ab0e9c801e94765c628c2400fec86d7ef42"
        },
        "date": 1795275182067,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 18.37556729005379,
            "unit": "iter/sec",
            "range": "stddev: 0.000290989195567239",
            "extra": "mean: 54.42008860000058 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.3992486949616705,
            "unit": "iter/sec",
            "range": "stddev: 0.0026983202464121144",
            "extra": "mean: 714.6692389999998 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 20.727693047954887,
            "unit": "iter/sec",
            "range": "stddev: 0.0005677764092681562",
            "extra": "mean: 48.244635699999705 msec\nrounds: 20"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 18.58017578150825,
            "unit": "iter/sec",
            "range": "stddev: 0.0013549818619907656",
            "extra": "mean: 53.82080405263124 msec\nrounds: 19"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 17.77688923179239,
            "unit": "iter/sec",
            "range": "stddev: 0.0004486569925068381",
            "extra": "mean: 56.25281155555544 msec\nrounds: 18"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 81.0911932908791,
            "unit": "iter/sec",
            "range": "stddev: 0.001822736047660981",
            "extra": "mean: 12.331795345678765 msec\nrounds: 81"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 21.562316287839657,
            "unit": "iter/sec",
            "range": "stddev: 0.0009329828277536658",
            "extra": "mean: 46.37720672727367 msec\nrounds: 22"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 32.160060515246045,
            "unit": "iter/sec",
            "range": "stddev: 0.0065435293532445605",
            "extra": "mean: 31.094468852940505 msec\nrounds: 34"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 58.991898175957445,
            "unit": "iter/sec",
            "range": "stddev: 0.0010048080162074512",
            "extra": "mean: 16.951480303570854 msec\nrounds: 56"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 81.43838550172447,
            "unit": "iter/sec",
            "range": "stddev: 0.002427048550156453",
            "extra": "mean: 12.279221817073289 msec\nrounds: 82"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 31.89218098750918,
            "unit": "iter/sec",
            "range": "stddev: 0.000307190192228965",
            "extra": "mean: 31.355647968750013 msec\nrounds: 32"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 29864.15456213255,
            "unit": "iter/sec",
            "range": "stddev: 0.0000026940536149345897",
            "extra": "mean: 33.48495929859639 usec\nrounds: 15626"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 25358.116714737072,
            "unit": "iter/sec",
            "range": "stddev: 0.0000046827774722286175",
            "extra": "mean: 39.43510518739911 usec\nrounds: 9716"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 35907.84130740032,
            "unit": "iter/sec",
            "range": "stddev: 0.0000026262823137204962",
            "extra": "mean: 27.849070386581772 usec\nrounds: 12545"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 22862.37183694316,
            "unit": "iter/sec",
            "range": "stddev: 0.00001107791472287253",
            "extra": "mean: 43.739993694972036 usec\nrounds: 9992"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 60161.24641182768,
            "unit": "iter/sec",
            "range": "stddev: 0.000001998141410237582",
            "extra": "mean: 16.621996046335244 usec\nrounds: 21246"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 55458.14044012425,
            "unit": "iter/sec",
            "range": "stddev: 0.0000021567836156371854",
            "extra": "mean: 18.031617938572186 usec\nrounds: 18162"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 23556.872084657698,
            "unit": "iter/sec",
            "range": "stddev: 0.00000869062873141254",
            "extra": "mean: 42.45045761619972 usec\nrounds: 9296"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 19715.064427365924,
            "unit": "iter/sec",
            "range": "stddev: 0.00001441518405592969",
            "extra": "mean: 50.722634140212506 usec\nrounds: 8014"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 3435.5816520869926,
            "unit": "iter/sec",
            "range": "stddev: 0.0001379382773047131",
            "extra": "mean: 291.0715276967834 usec\nrounds: 1715"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1305.4569749692657,
            "unit": "iter/sec",
            "range": "stddev: 0.000748242735851577",
            "extra": "mean: 766.0152875000289 usec\nrounds: 960"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 6726.471580408928,
            "unit": "iter/sec",
            "range": "stddev: 0.00048733781583530807",
            "extra": "mean: 148.6663532352583 usec\nrounds: 7001"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 71.11389758601541,
            "unit": "iter/sec",
            "range": "stddev: 0.0003397523197677207",
            "extra": "mean: 14.061948985294409 msec\nrounds: 68"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 47.98903591041296,
            "unit": "iter/sec",
            "range": "stddev: 0.003560915687246381",
            "extra": "mean: 20.83809314000021 msec\nrounds: 50"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 545.5749586220676,
            "unit": "iter/sec",
            "range": "stddev: 0.000061020822842829865",
            "extra": "mean: 1.8329287006237456 msec\nrounds: 481"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 185.8523146369468,
            "unit": "iter/sec",
            "range": "stddev: 0.004846359932852169",
            "extra": "mean: 5.380616334821818 msec\nrounds: 224"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 77.25257627530898,
            "unit": "iter/sec",
            "range": "stddev: 0.0007611779565065681",
            "extra": "mean: 12.944552119999836 msec\nrounds: 75"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 556.7788289415097,
            "unit": "iter/sec",
            "range": "stddev: 0.0017325512833933259",
            "extra": "mean: 1.7960453020476668 msec\nrounds: 586"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 1120.7706099371792,
            "unit": "iter/sec",
            "range": "stddev: 0.000024401338470434432",
            "extra": "mean: 892.2432397259699 usec\nrounds: 1022"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 11.76358766213078,
            "unit": "iter/sec",
            "range": "stddev: 0.0009628655158484472",
            "extra": "mean: 85.00807990909013 msec\nrounds: 11"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 32.56651628548087,
            "unit": "iter/sec",
            "range": "stddev: 0.000276843210660165",
            "extra": "mean: 30.706385393940028 msec\nrounds: 33"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 8.267439786683777,
            "unit": "iter/sec",
            "range": "stddev: 0.0075072146342354",
            "extra": "mean: 120.95642977777506 msec\nrounds: 9"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 14.586996188855728,
            "unit": "iter/sec",
            "range": "stddev: 0.007994304836087108",
            "extra": "mean: 68.55420999999895 msec\nrounds: 16"
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
          "id": "0e3324863946ba4aa62e70170b7f4993b0e87ba6",
          "message": "feat: complete the VM dynamic subset\n\n- give loop-created closures per-iteration cells via FRESH_LOCALS\n- support metaclasses, super proxies and extension methods/operators\n  with lexical extension scopes and imported-extension activation\n- run every example and core example on -t vm\n- update HIR design, bytecode proposal, roadmap and changelog\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-21T23:57:31+08:00",
          "tree_id": "2cb237ca4101c14130b213792a40f212f8fd9213",
          "url": "https://github.com/fyabc/oort-lang/commit/0e3324863946ba4aa62e70170b7f4993b0e87ba6"
        },
        "date": 1795276702943,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 21.01341161664131,
            "unit": "iter/sec",
            "range": "stddev: 0.0008135822975012943",
            "extra": "mean: 47.58865519999915 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.5763623179073794,
            "unit": "iter/sec",
            "range": "stddev: 0.0067610207349481635",
            "extra": "mean: 634.3719261999994 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 24.3478031873178,
            "unit": "iter/sec",
            "range": "stddev: 0.0003881808916361659",
            "extra": "mean: 41.07146720000088 msec\nrounds: 25"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 21.093178946373413,
            "unit": "iter/sec",
            "range": "stddev: 0.001286410612014364",
            "extra": "mean: 47.408690863637304 msec\nrounds: 22"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 20.131115343278022,
            "unit": "iter/sec",
            "range": "stddev: 0.0005907239258702563",
            "extra": "mean: 49.67434654999927 msec\nrounds: 20"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 85.74983396269609,
            "unit": "iter/sec",
            "range": "stddev: 0.0020649632906278004",
            "extra": "mean: 11.661830160919399 msec\nrounds: 87"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 25.463025849563206,
            "unit": "iter/sec",
            "range": "stddev: 0.0006203181931210039",
            "extra": "mean: 39.27263028000084 msec\nrounds: 25"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 40.25513896273649,
            "unit": "iter/sec",
            "range": "stddev: 0.000250924443232764",
            "extra": "mean: 24.841548825000537 msec\nrounds: 40"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 75.23989740572034,
            "unit": "iter/sec",
            "range": "stddev: 0.00024866047093120673",
            "extra": "mean: 13.290820887323166 msec\nrounds: 71"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 84.87085539444318,
            "unit": "iter/sec",
            "range": "stddev: 0.002771305455020989",
            "extra": "mean: 11.782607767441847 msec\nrounds: 86"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 37.324661476165,
            "unit": "iter/sec",
            "range": "stddev: 0.00046796293695349926",
            "extra": "mean: 26.79193756756738 msec\nrounds: 37"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 31261.358358407266,
            "unit": "iter/sec",
            "range": "stddev: 0.000003054687873165347",
            "extra": "mean: 31.988373266930203 usec\nrounds: 13055"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 28560.228691366043,
            "unit": "iter/sec",
            "range": "stddev: 0.000005089161714530153",
            "extra": "mean: 35.013725233310446 usec\nrounds: 10074"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 44337.27416840399,
            "unit": "iter/sec",
            "range": "stddev: 0.000002751623533930531",
            "extra": "mean: 22.554386095134117 usec\nrounds: 9565"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 25328.29079912286,
            "unit": "iter/sec",
            "range": "stddev: 0.000011040162642939948",
            "extra": "mean: 39.48154290911058 usec\nrounds: 8250"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 60534.54293643255,
            "unit": "iter/sec",
            "range": "stddev: 0.000001967751449226607",
            "extra": "mean: 16.519493688919102 usec\nrounds: 18222"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 59907.62385157181,
            "unit": "iter/sec",
            "range": "stddev: 0.000002105449849467378",
            "extra": "mean: 16.692366275077404 usec\nrounds: 14642"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 27608.040664744538,
            "unit": "iter/sec",
            "range": "stddev: 0.000007123290502055864",
            "extra": "mean: 36.22133175415812 usec\nrounds: 7810"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 22999.72284564119,
            "unit": "iter/sec",
            "range": "stddev: 0.000008747667560969898",
            "extra": "mean: 43.478784797161836 usec\nrounds: 7788"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 4947.062785495206,
            "unit": "iter/sec",
            "range": "stddev: 0.000036987333528025466",
            "extra": "mean: 202.1401472671827 usec\nrounds: 1976"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1336.7044870021662,
            "unit": "iter/sec",
            "range": "stddev: 0.0009926563694035466",
            "extra": "mean: 748.1085084428086 usec\nrounds: 1066"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 7238.428445540154,
            "unit": "iter/sec",
            "range": "stddev: 0.0007364582560315509",
            "extra": "mean: 138.15153489790103 usec\nrounds: 3281"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 68.74332038577437,
            "unit": "iter/sec",
            "range": "stddev: 0.00364555915986488",
            "extra": "mean: 14.54686789041017 msec\nrounds: 73"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 55.05585734077522,
            "unit": "iter/sec",
            "range": "stddev: 0.0006233733711748199",
            "extra": "mean: 18.163371679245188 msec\nrounds: 53"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 590.6351485381178,
            "unit": "iter/sec",
            "range": "stddev: 0.00004316863150508585",
            "extra": "mean: 1.6930926012024545 msec\nrounds: 499"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 195.27494517004453,
            "unit": "iter/sec",
            "range": "stddev: 0.007145025171020633",
            "extra": "mean: 5.12098466666681 msec\nrounds: 30"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 77.10505239547959,
            "unit": "iter/sec",
            "range": "stddev: 0.003604366737887596",
            "extra": "mean: 12.969318727272231 msec\nrounds: 77"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 669.3904322988224,
            "unit": "iter/sec",
            "range": "stddev: 0.0021644800391182203",
            "extra": "mean: 1.4938964642291008 msec\nrounds: 629"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 1460.8078541181944,
            "unit": "iter/sec",
            "range": "stddev: 0.000021798978275278842",
            "extra": "mean: 684.5527268907261 usec\nrounds: 1190"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 13.303779035962332,
            "unit": "iter/sec",
            "range": "stddev: 0.0004223480030256559",
            "extra": "mean: 75.16661223076791 msec\nrounds: 13"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 40.924396842213156,
            "unit": "iter/sec",
            "range": "stddev: 0.0003259492076548427",
            "extra": "mean: 24.435302097562225 msec\nrounds: 41"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 8.43794075508215,
            "unit": "iter/sec",
            "range": "stddev: 0.0010289369752570232",
            "extra": "mean: 118.51232771428296 msec\nrounds: 7"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 14.89717915551635,
            "unit": "iter/sec",
            "range": "stddev: 0.010838731123756077",
            "extra": "mean: 67.12680229999819 msec\nrounds: 10"
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
          "id": "98aa94834570a2072b33e319c4f7f5a95a801a56",
          "message": "benchmarks: refresh 0.4.0 results\n\nRegenerate the current result snapshot and append the 0.4.0 milestone.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-22T00:10:58+08:00",
          "tree_id": "d3de3fe25907cb4d71c48caa55adbd971381211f",
          "url": "https://github.com/fyabc/oort-lang/commit/98aa94834570a2072b33e319c4f7f5a95a801a56"
        },
        "date": 1795277509585,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 24.809362275962414,
            "unit": "iter/sec",
            "range": "stddev: 0.0002723712519951362",
            "extra": "mean: 40.307364166667504 msec\nrounds: 6"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.142904527374301,
            "unit": "iter/sec",
            "range": "stddev: 0.0016601947917206474",
            "extra": "mean: 466.65634760000216 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 33.01516207335349,
            "unit": "iter/sec",
            "range": "stddev: 0.00020858208483743253",
            "extra": "mean: 30.28911376470568 msec\nrounds: 34"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 30.760016411679107,
            "unit": "iter/sec",
            "range": "stddev: 0.00029909073202633187",
            "extra": "mean: 32.509735580645376 msec\nrounds: 31"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 29.77144710140509,
            "unit": "iter/sec",
            "range": "stddev: 0.0003563344977412202",
            "extra": "mean: 33.58923053333219 msec\nrounds: 30"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 117.0487854433872,
            "unit": "iter/sec",
            "range": "stddev: 0.00013578861419337356",
            "extra": "mean: 8.543446189654556 msec\nrounds: 116"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 35.63769713937767,
            "unit": "iter/sec",
            "range": "stddev: 0.00016904256311834492",
            "extra": "mean: 28.060174485714892 msec\nrounds: 35"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 56.433163752852934,
            "unit": "iter/sec",
            "range": "stddev: 0.00015413832312996415",
            "extra": "mean: 17.720076874999688 msec\nrounds: 56"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 88.63273094671155,
            "unit": "iter/sec",
            "range": "stddev: 0.00019644756809573821",
            "extra": "mean: 11.282513686746578 msec\nrounds: 83"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 114.61237849780073,
            "unit": "iter/sec",
            "range": "stddev: 0.0018142211994379449",
            "extra": "mean: 8.725061054545595 msec\nrounds: 110"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 50.928365332672705,
            "unit": "iter/sec",
            "range": "stddev: 0.00014232308114813931",
            "extra": "mean: 19.635423078432435 msec\nrounds: 51"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 40317.157394910806,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019357142082746807",
            "extra": "mean: 24.803335964509962 usec\nrounds: 19636"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 38973.13773723311,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016067252100257036",
            "extra": "mean: 25.65869873609501 usec\nrounds: 15903"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 63681.94646363942,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012956717701977786",
            "extra": "mean: 15.703037603773176 usec\nrounds: 15424"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 40199.95359061731,
            "unit": "iter/sec",
            "range": "stddev: 0.000010019596401463209",
            "extra": "mean: 24.87565060854698 usec\nrounds: 11832"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 83681.9486483161,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010312551161964915",
            "extra": "mean: 11.950008528154925 usec\nrounds: 24976"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 78518.52819048482,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011780876999781544",
            "extra": "mean: 12.735847487793128 usec\nrounds: 23008"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 40470.4003074892,
            "unit": "iter/sec",
            "range": "stddev: 0.000006461266723124683",
            "extra": "mean: 24.70941706536434 usec\nrounds: 11075"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 35463.98734833523,
            "unit": "iter/sec",
            "range": "stddev: 0.000006409545094818498",
            "extra": "mean: 28.197618902177467 usec\nrounds: 10803"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 7617.09206905697,
            "unit": "iter/sec",
            "range": "stddev: 0.00002601186847651963",
            "extra": "mean: 131.28369605276472 usec\nrounds: 3040"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1795.4647423975343,
            "unit": "iter/sec",
            "range": "stddev: 0.000820845539655878",
            "extra": "mean: 556.9588621744095 usec\nrounds: 1306"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 8821.64669155648,
            "unit": "iter/sec",
            "range": "stddev: 0.0005531896321511795",
            "extra": "mean: 113.35752098949243 usec\nrounds: 11077"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 97.45610847117295,
            "unit": "iter/sec",
            "range": "stddev: 0.0029476138750005455",
            "extra": "mean: 10.261029459182593 msec\nrounds: 98"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 74.1715240920382,
            "unit": "iter/sec",
            "range": "stddev: 0.0002414098065382133",
            "extra": "mean: 13.482263068494005 msec\nrounds: 73"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 786.5043910429681,
            "unit": "iter/sec",
            "range": "stddev: 0.00005635722028095902",
            "extra": "mean: 1.271448718390395 msec\nrounds: 696"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 224.1191607072793,
            "unit": "iter/sec",
            "range": "stddev: 0.005066061442928249",
            "extra": "mean: 4.461912122302181 msec\nrounds: 278"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 103.20564571195426,
            "unit": "iter/sec",
            "range": "stddev: 0.002811505121229881",
            "extra": "mean: 9.689392407766027 msec\nrounds: 103"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 737.38339092996,
            "unit": "iter/sec",
            "range": "stddev: 0.0017756464149898275",
            "extra": "mean: 1.356146629148831 msec\nrounds: 693"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 1614.667052137515,
            "unit": "iter/sec",
            "range": "stddev: 0.00003122149010014847",
            "extra": "mean: 619.3227258066538 usec\nrounds: 1426"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 18.17443590089677,
            "unit": "iter/sec",
            "range": "stddev: 0.0006817985380277844",
            "extra": "mean: 55.022340470586904 msec\nrounds: 17"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 49.27045372204523,
            "unit": "iter/sec",
            "range": "stddev: 0.0001670671202090129",
            "extra": "mean: 20.296139459997846 msec\nrounds: 50"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 11.041604436107244,
            "unit": "iter/sec",
            "range": "stddev: 0.01074291196949059",
            "extra": "mean: 90.56654816666783 msec\nrounds: 12"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 17.774989761278672,
            "unit": "iter/sec",
            "range": "stddev: 0.007379577907303877",
            "extra": "mean: 56.25882284210461 msec\nrounds: 19"
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
          "id": "27da7ca9a452af3612808de3dc214a13d4fa09f3",
          "message": "ci: add Trusted Publishing workflow for PyPI\n\n- upgrade actions/setup-node to v7\n- build, check and publish distributions via PyPI OIDC\n- support manual TestPyPI/PyPI runs and release-triggered PyPI publishes\n- document the publisher setup and release checklist\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-22T00:22:23+08:00",
          "tree_id": "672c4834ab16ac7766477810b4952047d4839663",
          "url": "https://github.com/fyabc/oort-lang/commit/27da7ca9a452af3612808de3dc214a13d4fa09f3"
        },
        "date": 1795278188450,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 27.543762040656503,
            "unit": "iter/sec",
            "range": "stddev: 0.0010208721669690444",
            "extra": "mean: 36.30586114285807 msec\nrounds: 7"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.901897785806733,
            "unit": "iter/sec",
            "range": "stddev: 0.005087154967308609",
            "extra": "mean: 525.7906115999958 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 29.403876481815594,
            "unit": "iter/sec",
            "range": "stddev: 0.0009266944712197889",
            "extra": "mean: 34.009121233332465 msec\nrounds: 30"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 25.94418641589889,
            "unit": "iter/sec",
            "range": "stddev: 0.0008168350626797013",
            "extra": "mean: 38.544280555554 msec\nrounds: 27"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 24.67566759019354,
            "unit": "iter/sec",
            "range": "stddev: 0.000522602583466318",
            "extra": "mean: 40.52575259999912 msec\nrounds: 25"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 110.88408087240212,
            "unit": "iter/sec",
            "range": "stddev: 0.00013808882853578468",
            "extra": "mean: 9.018427100917508 msec\nrounds: 109"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 31.06952259295151,
            "unit": "iter/sec",
            "range": "stddev: 0.00045872655420543964",
            "extra": "mean: 32.18588238709731 msec\nrounds: 31"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 50.38454300686691,
            "unit": "iter/sec",
            "range": "stddev: 0.0003221211172462367",
            "extra": "mean: 19.847356755100666 msec\nrounds: 49"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 91.27765916299954,
            "unit": "iter/sec",
            "range": "stddev: 0.0002237446420476134",
            "extra": "mean: 10.95558331764671 msec\nrounds: 85"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 107.08828140821967,
            "unit": "iter/sec",
            "range": "stddev: 0.0019301324472387564",
            "extra": "mean: 9.33808990909106 msec\nrounds: 110"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 45.804846117074234,
            "unit": "iter/sec",
            "range": "stddev: 0.0003424559897032602",
            "extra": "mean: 21.83175110869414 msec\nrounds: 46"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 37094.36966629191,
            "unit": "iter/sec",
            "range": "stddev: 0.0000027582921157300524",
            "extra": "mean: 26.958269111894676 usec\nrounds: 16822"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 36139.38602510841,
            "unit": "iter/sec",
            "range": "stddev: 0.0000026806796683451972",
            "extra": "mean: 27.670641645799797 usec\nrounds: 14388"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 54611.43541534352,
            "unit": "iter/sec",
            "range": "stddev: 0.000001991362266687737",
            "extra": "mean: 18.31118322370706 usec\nrounds: 12160"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 30072.060827172852,
            "unit": "iter/sec",
            "range": "stddev: 0.000012631400042588213",
            "extra": "mean: 33.25345761127248 usec\nrounds: 8599"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 76433.74513908672,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014757178771115532",
            "extra": "mean: 13.083226501335199 usec\nrounds: 22746"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 72902.02113018566,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015318625753748972",
            "extra": "mean: 13.717040824070404 usec\nrounds: 18445"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 33277.5218648767,
            "unit": "iter/sec",
            "range": "stddev: 0.000005932826184566715",
            "extra": "mean: 30.050314565504536 usec\nrounds: 9804"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 27536.18818849489,
            "unit": "iter/sec",
            "range": "stddev: 0.000007148207767574269",
            "extra": "mean: 36.315847101081985 usec\nrounds: 9176"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 6046.832981528879,
            "unit": "iter/sec",
            "range": "stddev: 0.000028964080591618163",
            "extra": "mean: 165.37582616465127 usec\nrounds: 2790"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1631.5243759488098,
            "unit": "iter/sec",
            "range": "stddev: 0.0006801226200238552",
            "extra": "mean: 612.9237262657824 usec\nrounds: 1264"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 8927.85465773263,
            "unit": "iter/sec",
            "range": "stddev: 0.0004460833661343069",
            "extra": "mean: 112.00899189525626 usec\nrounds: 4195"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 87.48251815963027,
            "unit": "iter/sec",
            "range": "stddev: 0.002898045838041203",
            "extra": "mean: 11.43085522727283 msec\nrounds: 88"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 62.820459433191985,
            "unit": "iter/sec",
            "range": "stddev: 0.002854451116174256",
            "extra": "mean: 15.918380874999416 msec\nrounds: 64"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 697.4207067139358,
            "unit": "iter/sec",
            "range": "stddev: 0.000038476363582591804",
            "extra": "mean: 1.4338547599364218 msec\nrounds: 629"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 254.1283459467771,
            "unit": "iter/sec",
            "range": "stddev: 0.00424347041290874",
            "extra": "mean: 3.9350195125790224 msec\nrounds: 318"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 91.51761938244015,
            "unit": "iter/sec",
            "range": "stddev: 0.000155070003911277",
            "extra": "mean: 10.926857655913569 msec\nrounds: 93"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 788.1917818593656,
            "unit": "iter/sec",
            "range": "stddev: 0.0017995625750891011",
            "extra": "mean: 1.268726752822737 msec\nrounds: 797"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 1784.9081085852808,
            "unit": "iter/sec",
            "range": "stddev: 0.000018204388165856978",
            "extra": "mean: 560.2529313358325 usec\nrounds: 1602"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 16.088487016448745,
            "unit": "iter/sec",
            "range": "stddev: 0.0007247578434592831",
            "extra": "mean: 62.156248687499804 msec\nrounds: 16"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 51.56783853204742,
            "unit": "iter/sec",
            "range": "stddev: 0.00074850094626574",
            "extra": "mean: 19.391931647058247 msec\nrounds: 51"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 10.419745395548809,
            "unit": "iter/sec",
            "range": "stddev: 0.007221485279235529",
            "extra": "mean: 95.97163481817782 msec\nrounds: 11"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 19.245875604047292,
            "unit": "iter/sec",
            "range": "stddev: 0.006186966369552047",
            "extra": "mean: 51.95918442856952 msec\nrounds: 14"
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
          "id": "bb2b6738a896965bd564cc5cc3b2fbbbf22252c2",
          "message": "docs: add PyPI badge and installation instructions\n\n- link the PyPI package from the README and docs home\n- make pip install oort-lang the recommended install path\n- refresh the VM implementation status in the README\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-22T00:56:19+08:00",
          "tree_id": "2549bbfa83fdd175a9f7dd123f524475d2619fe6",
          "url": "https://github.com/fyabc/oort-lang/commit/bb2b6738a896965bd564cc5cc3b2fbbbf22252c2"
        },
        "date": 1795280227051,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 17.62847851087579,
            "unit": "iter/sec",
            "range": "stddev: 0.000268749229805602",
            "extra": "mean: 56.726393000000286 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.3757246511631605,
            "unit": "iter/sec",
            "range": "stddev: 0.006397364940831238",
            "extra": "mean: 726.8896426000005 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 20.081807680710785,
            "unit": "iter/sec",
            "range": "stddev: 0.0013295404997318292",
            "extra": "mean: 49.79631395238047 msec\nrounds: 21"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 18.376105491998768,
            "unit": "iter/sec",
            "range": "stddev: 0.0007401551079741503",
            "extra": "mean: 54.41849473684263 msec\nrounds: 19"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 17.080286117376456,
            "unit": "iter/sec",
            "range": "stddev: 0.0018748871326925746",
            "extra": "mean: 58.54702861111091 msec\nrounds: 18"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 81.4109499379958,
            "unit": "iter/sec",
            "range": "stddev: 0.001755119582768868",
            "extra": "mean: 12.283359925926671 msec\nrounds: 81"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 21.226256548221354,
            "unit": "iter/sec",
            "range": "stddev: 0.0008338157383280567",
            "extra": "mean: 47.11146299999821 msec\nrounds: 21"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 34.997895396091124,
            "unit": "iter/sec",
            "range": "stddev: 0.00031826275980832453",
            "extra": "mean: 28.573146718750664 msec\nrounds: 32"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 58.956891820878745,
            "unit": "iter/sec",
            "range": "stddev: 0.0002907893482092543",
            "extra": "mean: 16.961545446428442 msec\nrounds: 56"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 80.73127853331796,
            "unit": "iter/sec",
            "range": "stddev: 0.0029476650110555032",
            "extra": "mean: 12.38677273749973 msec\nrounds: 80"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 31.108656587411275,
            "unit": "iter/sec",
            "range": "stddev: 0.00044145118791017064",
            "extra": "mean: 32.14539326666615 msec\nrounds: 30"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 29665.1671302494,
            "unit": "iter/sec",
            "range": "stddev: 0.000002684093745196206",
            "extra": "mean: 33.7095690581937 usec\nrounds: 15248"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 25875.992526126884,
            "unit": "iter/sec",
            "range": "stddev: 0.0000034899455691164673",
            "extra": "mean: 38.645860598015865 usec\nrounds: 9799"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 35984.42208362592,
            "unit": "iter/sec",
            "range": "stddev: 0.000003375445438772147",
            "extra": "mean: 27.789802978523657 usec\nrounds: 12288"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 22246.28817364019,
            "unit": "iter/sec",
            "range": "stddev: 0.000010266452547457712",
            "extra": "mean: 44.95131916815265 usec\nrounds: 8848"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 57621.82814347911,
            "unit": "iter/sec",
            "range": "stddev: 0.0000022790457163688226",
            "extra": "mean: 17.354534422441212 usec\nrounds: 19159"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 53000.8144392549,
            "unit": "iter/sec",
            "range": "stddev: 0.0000023405485595551394",
            "extra": "mean: 18.867634593542263 usec\nrounds: 14945"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 21191.96637268858,
            "unit": "iter/sec",
            "range": "stddev: 0.00002316477329008044",
            "extra": "mean: 47.18769284613262 usec\nrounds: 8429"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 17920.88832339803,
            "unit": "iter/sec",
            "range": "stddev: 0.000030628741157048466",
            "extra": "mean: 55.80080529235658 usec\nrounds: 8654"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 4336.1375075360575,
            "unit": "iter/sec",
            "range": "stddev: 0.00003632885042272758",
            "extra": "mean: 230.6199926229356 usec\nrounds: 2440"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1273.0944718552314,
            "unit": "iter/sec",
            "range": "stddev: 0.0009061047631700822",
            "extra": "mean: 785.4876618407891 usec\nrounds: 967"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 6431.772130673339,
            "unit": "iter/sec",
            "range": "stddev: 0.0007142162233263042",
            "extra": "mean: 155.4781450093616 usec\nrounds: 3186"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 67.26917077269383,
            "unit": "iter/sec",
            "range": "stddev: 0.0010536228992151177",
            "extra": "mean: 14.865650765624183 msec\nrounds: 64"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 44.864187535271185,
            "unit": "iter/sec",
            "range": "stddev: 0.0038573466650514603",
            "extra": "mean: 22.2894931333332 msec\nrounds: 45"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 516.2949954091646,
            "unit": "iter/sec",
            "range": "stddev: 0.00005812324213699438",
            "extra": "mean: 1.9368771901565662 msec\nrounds: 447"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 169.85863553838524,
            "unit": "iter/sec",
            "range": "stddev: 0.00630773982412371",
            "extra": "mean: 5.887248515981494 msec\nrounds: 219"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 70.52069891405503,
            "unit": "iter/sec",
            "range": "stddev: 0.002800769770897157",
            "extra": "mean: 14.18023382352917 msec\nrounds: 68"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 557.8463104902544,
            "unit": "iter/sec",
            "range": "stddev: 0.0019262119298890338",
            "extra": "mean: 1.7926084320987365 msec\nrounds: 567"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 982.7514232686189,
            "unit": "iter/sec",
            "range": "stddev: 0.00003343502597198763",
            "extra": "mean: 1.0175513118810986 msec\nrounds: 1010"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 11.318466212418254,
            "unit": "iter/sec",
            "range": "stddev: 0.001092542698664793",
            "extra": "mean: 88.35119363636323 msec\nrounds: 11"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 37.334475657668534,
            "unit": "iter/sec",
            "range": "stddev: 0.00023610661090830453",
            "extra": "mean: 26.78489472222169 msec\nrounds: 36"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 8.034019678730678,
            "unit": "iter/sec",
            "range": "stddev: 0.010654826685138322",
            "extra": "mean: 124.47069337499971 msec\nrounds: 8"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 13.502268580955212,
            "unit": "iter/sec",
            "range": "stddev: 0.008567638695211354",
            "extra": "mean: 74.06162853333313 msec\nrounds: 15"
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
          "id": "6e7009f8f35165ba0c1035f2cea2a2f61e13b749",
          "message": "feat(core): infer function return types (OP 0005 first slice)\n\nTop-level def and do-lambdas in oort-core may now omit the return\nannotation; the checker infers it by joining the collected return\nexpression types with the fall-through body type. Lambdas also accept a\nreturn type pushed down from an expected function type via the existing\ndefault_return hook (val f: (Int) -> Int = do(x: Int) { x }).\n\nDesign decisions (user-confirmed):\n- Self-recursive functions still require an explicit return annotation:\n  inference cannot see through the recursive call (the placeholder\n  Unknown collapses through arithmetic/join), matching Kotlin/Scala,\n  which both mandate result types on recursive functions. Detected via\n  _mark_recursive_call hitting an active inference frame.\n- Scope is top-level def + lambda; class methods keep requiring\n  annotations (two-pass checking + inter-method recursion makes\n  inference substantially harder) and __init__ stays Unit.\n\nImplementation reuses the existing infer mode (expected=Unknown),\njoin_types, Never/saw_never and Unknown cascade suppression. A\n_ReturnInfer frame stack parallel to function-body nesting collects\nreturn types; the frozen FunctionType is rebuilt and backfilled into\nNameInfo.type and node.metadata so inferred types export across modules.\n\nDocs: new design/14-core-typechecking.md documents the as-implemented\nbidirectional checking / local inference algorithm with a cross-language\nreturn-inference comparison (registered in mkdocs + design index);\nspec 11, implementation 09, OP 0005, OP 0017, roadmap, conformance 06 and\nexamples.md updated. mathlib.ort drops return annotations on add/square\nto demonstrate inferred cross-module exports. 1044 tests pass.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-22T04:40:21+08:00",
          "tree_id": "b902ee8dc4fbb6d4b66cfd9fb92940945c8a69a2",
          "url": "https://github.com/fyabc/oort-lang/commit/6e7009f8f35165ba0c1035f2cea2a2f61e13b749"
        },
        "date": 1795293834205,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 18.493452014198372,
            "unit": "iter/sec",
            "range": "stddev: 0.00037212147367563176",
            "extra": "mean: 54.073193000000686 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.544962033243997,
            "unit": "iter/sec",
            "range": "stddev: 0.013748149215566855",
            "extra": "mean: 647.2650967999997 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 25.31984904905902,
            "unit": "iter/sec",
            "range": "stddev: 0.0002647227735062999",
            "extra": "mean: 39.49470623076893 msec\nrounds: 26"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 21.64305197656832,
            "unit": "iter/sec",
            "range": "stddev: 0.005731748349570202",
            "extra": "mean: 46.204204521739456 msec\nrounds: 23"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 21.2187880296445,
            "unit": "iter/sec",
            "range": "stddev: 0.0002715058199410804",
            "extra": "mean: 47.12804513636277 msec\nrounds: 22"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 97.65282468607847,
            "unit": "iter/sec",
            "range": "stddev: 0.0017083898959445625",
            "extra": "mean: 10.240359182795471 msec\nrounds: 93"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 25.044172460591003,
            "unit": "iter/sec",
            "range": "stddev: 0.00033670353572185755",
            "extra": "mean: 39.92944871999981 msec\nrounds: 25"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 38.87196984696415,
            "unit": "iter/sec",
            "range": "stddev: 0.00030117670841378055",
            "extra": "mean: 25.725477868420878 msec\nrounds: 38"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 64.13316391870163,
            "unit": "iter/sec",
            "range": "stddev: 0.0006587883221013108",
            "extra": "mean: 15.592556781818056 msec\nrounds: 55"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 98.001830971301,
            "unit": "iter/sec",
            "range": "stddev: 0.0019341055263834238",
            "extra": "mean: 10.203890989473875 msec\nrounds: 95"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 43.12430328452647,
            "unit": "iter/sec",
            "range": "stddev: 0.000306460789242628",
            "extra": "mean: 23.188780428571288 msec\nrounds: 42"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 30457.429510777103,
            "unit": "iter/sec",
            "range": "stddev: 0.000003008117163636978",
            "extra": "mean: 32.83271162611272 usec\nrounds: 15577"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 30951.070480061026,
            "unit": "iter/sec",
            "range": "stddev: 0.0000028606992213263546",
            "extra": "mean: 32.309060219555555 usec\nrounds: 16307"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 41974.86901096894,
            "unit": "iter/sec",
            "range": "stddev: 0.0000024179432489189625",
            "extra": "mean: 23.823778931595438 usec\nrounds: 15312"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 27448.61747881181,
            "unit": "iter/sec",
            "range": "stddev: 0.00000950726870176439",
            "extra": "mean: 36.43170738096088 usec\nrounds: 12600"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 74802.90667399274,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014471699070144452",
            "extra": "mean: 13.36846446834234 usec\nrounds: 26596"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 70003.59729827347,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014514311371311742",
            "extra": "mean: 14.284980180935122 usec\nrounds: 22655"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 27478.025719572215,
            "unit": "iter/sec",
            "range": "stddev: 0.000008706945906032422",
            "extra": "mean: 36.39271650028749 usec\nrounds: 11418"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 23065.12234399255,
            "unit": "iter/sec",
            "range": "stddev: 0.000010766470588099787",
            "extra": "mean: 43.35550382460712 usec\nrounds: 11766"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 3980.5083553328514,
            "unit": "iter/sec",
            "range": "stddev: 0.00004065791013602784",
            "extra": "mean: 251.2241931762959 usec\nrounds: 2081"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1327.289724417077,
            "unit": "iter/sec",
            "range": "stddev: 0.0008015335339547992",
            "extra": "mean: 753.4150092506616 usec\nrounds: 1081"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program_vm",
            "value": 1195.5332768897385,
            "unit": "iter/sec",
            "range": "stddev: 0.0001895255423462224",
            "extra": "mean: 836.4468135939875 usec\nrounds: 971"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 7145.136715851396,
            "unit": "iter/sec",
            "range": "stddev: 0.0004285590586010774",
            "extra": "mean: 139.9553346238306 usec\nrounds: 9040"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_empty",
            "value": 82719.72065320029,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015035259518296138",
            "extra": "mean: 12.089015679736965 usec\nrounds: 28253"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_fib",
            "value": 10324.100801412353,
            "unit": "iter/sec",
            "range": "stddev: 0.000007447831689378453",
            "extra": "mean: 96.86073579049118 usec\nrounds: 4504"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_empty",
            "value": 84741.8944472336,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012875772574621149",
            "extra": "mean: 11.800538641753779 usec\nrounds: 30731"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_fib",
            "value": 13277.668871579772,
            "unit": "iter/sec",
            "range": "stddev: 0.000005460600907176547",
            "extra": "mean: 75.31442527087366 usec\nrounds: 6276"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 80.2785323373752,
            "unit": "iter/sec",
            "range": "stddev: 0.0027038338193300458",
            "extra": "mean: 12.45663032051261 msec\nrounds: 78"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 56.400535791304634,
            "unit": "iter/sec",
            "range": "stddev: 0.000521602470461171",
            "extra": "mean: 17.730328018518076 msec\nrounds: 54"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 615.6223091976302,
            "unit": "iter/sec",
            "range": "stddev: 0.00005089502484831235",
            "extra": "mean: 1.6243725821166999 msec\nrounds: 548"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 207.38962525810732,
            "unit": "iter/sec",
            "range": "stddev: 0.004078168047423536",
            "extra": "mean: 4.821841973799063 msec\nrounds: 229"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 86.808542753592,
            "unit": "iter/sec",
            "range": "stddev: 0.0022120567895605116",
            "extra": "mean: 11.51960358139547 msec\nrounds: 86"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 627.6186921268887,
            "unit": "iter/sec",
            "range": "stddev: 0.001207817559110618",
            "extra": "mean: 1.5933241194763925 msec\nrounds: 611"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 43653.673659182066,
            "unit": "iter/sec",
            "range": "stddev: 0.0000023087175054324924",
            "extra": "mean: 22.90757950424319 usec\nrounds: 19848"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 12.43187218787213,
            "unit": "iter/sec",
            "range": "stddev: 0.0019066739169810406",
            "extra": "mean: 80.43840741666781 msec\nrounds: 12"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 42.252578935450025,
            "unit": "iter/sec",
            "range": "stddev: 0.0001681288599803848",
            "extra": "mean: 23.667194410256396 msec\nrounds: 39"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 9.618341413764508,
            "unit": "iter/sec",
            "range": "stddev: 0.007263859414348033",
            "extra": "mean: 103.96802909999963 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 18.401965009862053,
            "unit": "iter/sec",
            "range": "stddev: 0.0052772173053590695",
            "extra": "mean: 54.34202268421205 msec\nrounds: 19"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_methods",
            "value": 8.880017799344367,
            "unit": "iter/sec",
            "range": "stddev: 0.0011616999053701564",
            "extra": "mean: 112.61238688889028 msec\nrounds: 9"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_methods",
            "value": 11.056531670509143,
            "unit": "iter/sec",
            "range": "stddev: 0.0007136431630392462",
            "extra": "mean: 90.44427581818258 msec\nrounds: 11"
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
          "id": "9b7008033d1929651d93d6fc38971c9911c1fff3",
          "message": "docs: fix MD038 trailing space in code span (OP 0020)\n\nThe Quality and security CI job failed markdownlint on a code span with\na trailing space (`x = `); drop the space. No content change.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-22T04:59:27+08:00",
          "tree_id": "ad1f412a855c6ad6b5432c8428c61ad6bf2797a6",
          "url": "https://github.com/fyabc/oort-lang/commit/9b7008033d1929651d93d6fc38971c9911c1fff3"
        },
        "date": 1795294928860,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 16.602331470056885,
            "unit": "iter/sec",
            "range": "stddev: 0.001955729899308753",
            "extra": "mean: 60.23250420000039 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.5725096346462353,
            "unit": "iter/sec",
            "range": "stddev: 0.00848894855184353",
            "extra": "mean: 635.9261513999996 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 25.37170478653867,
            "unit": "iter/sec",
            "range": "stddev: 0.0008637630546839122",
            "extra": "mean: 39.413985319999654 msec\nrounds: 25"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 21.93264659120848,
            "unit": "iter/sec",
            "range": "stddev: 0.0015995244474296462",
            "extra": "mean: 45.594132739130615 msec\nrounds: 23"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 21.061026958239328,
            "unit": "iter/sec",
            "range": "stddev: 0.0014572929307759567",
            "extra": "mean: 47.4810654761917 msec\nrounds: 21"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 99.09687162196803,
            "unit": "iter/sec",
            "range": "stddev: 0.0017912973390455736",
            "extra": "mean: 10.09113591208784 msec\nrounds: 91"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 24.63640765798477,
            "unit": "iter/sec",
            "range": "stddev: 0.0005777600248496628",
            "extra": "mean: 40.59033337499981 msec\nrounds: 24"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 38.120036469251566,
            "unit": "iter/sec",
            "range": "stddev: 0.0006858983764408162",
            "extra": "mean: 26.232923486487774 msec\nrounds: 37"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 64.53798391340938,
            "unit": "iter/sec",
            "range": "stddev: 0.00025761159335111595",
            "extra": "mean: 15.494751142857208 msec\nrounds: 56"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 98.35292564920677,
            "unit": "iter/sec",
            "range": "stddev: 0.002277848623799209",
            "extra": "mean: 10.16746571999981 msec\nrounds: 100"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 43.1062696710888,
            "unit": "iter/sec",
            "range": "stddev: 0.00038425134733179533",
            "extra": "mean: 23.1984815116279 msec\nrounds: 43"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 30915.83913245031,
            "unit": "iter/sec",
            "range": "stddev: 0.0000034904824153965484",
            "extra": "mean: 32.345879266474974 usec\nrounds: 15323"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 30873.91190125097,
            "unit": "iter/sec",
            "range": "stddev: 0.0000032676995040547416",
            "extra": "mean: 32.38980545123216 usec\nrounds: 13575"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 42812.62482663281,
            "unit": "iter/sec",
            "range": "stddev: 0.000003077180918627751",
            "extra": "mean: 23.357596130801152 usec\nrounds: 13336"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 27942.159595678964,
            "unit": "iter/sec",
            "range": "stddev: 0.000010752885785576979",
            "extra": "mean: 35.78821445693274 usec\nrounds: 8342"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 74880.05988658164,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015226055049630706",
            "extra": "mean: 13.354690174055245 usec\nrounds: 22461"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 71057.6885885743,
            "unit": "iter/sec",
            "range": "stddev: 0.000001813448396331157",
            "extra": "mean: 14.07307245511494 usec\nrounds: 21779"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 27609.45593422254,
            "unit": "iter/sec",
            "range": "stddev: 0.0000071315904954511284",
            "extra": "mean: 36.21947503719106 usec\nrounds: 9414"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 23705.395064458826,
            "unit": "iter/sec",
            "range": "stddev: 0.000008662916404940882",
            "extra": "mean: 42.1844899560137 usec\nrounds: 9558"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 4175.781435999378,
            "unit": "iter/sec",
            "range": "stddev: 0.00003436391643117852",
            "extra": "mean: 239.47613526393124 usec\nrounds: 2521"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1347.1513881508142,
            "unit": "iter/sec",
            "range": "stddev: 0.0008239289676550602",
            "extra": "mean: 742.3070701598457 usec\nrounds: 1126"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program_vm",
            "value": 1190.5735496771335,
            "unit": "iter/sec",
            "range": "stddev: 0.00018402003256920863",
            "extra": "mean: 839.9313089654861 usec\nrounds: 725"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 7001.645903748789,
            "unit": "iter/sec",
            "range": "stddev: 0.0005580211888795088",
            "extra": "mean: 142.8235608808187 usec\nrounds: 7720"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_empty",
            "value": 84041.54892757525,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014718388774622455",
            "extra": "mean: 11.898876362473676 usec\nrounds: 21652"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_fib",
            "value": 10251.091817828179,
            "unit": "iter/sec",
            "range": "stddev: 0.000005476471595128505",
            "extra": "mean: 97.55058463732134 usec\nrounds: 4218"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_empty",
            "value": 84734.34390830353,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012226389675818138",
            "extra": "mean: 11.801590168470108 usec\nrounds: 25225"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_fib",
            "value": 13248.909138238121,
            "unit": "iter/sec",
            "range": "stddev: 0.000004345696752398904",
            "extra": "mean: 75.47791214854561 usec\nrounds: 7433"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 77.81737646892599,
            "unit": "iter/sec",
            "range": "stddev: 0.0043930745359642255",
            "extra": "mean: 12.850600282050369 msec\nrounds: 78"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 56.45115089773694,
            "unit": "iter/sec",
            "range": "stddev: 0.00037530535916459594",
            "extra": "mean: 17.714430690908888 msec\nrounds: 55"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 621.3463960126797,
            "unit": "iter/sec",
            "range": "stddev: 0.0000468373339490055",
            "extra": "mean: 1.6094082244899561 msec\nrounds: 539"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 174.70176388214435,
            "unit": "iter/sec",
            "range": "stddev: 0.00719963856046",
            "extra": "mean: 5.724040660943816 msec\nrounds: 233"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 89.77507355496445,
            "unit": "iter/sec",
            "range": "stddev: 0.00008308323762260897",
            "extra": "mean: 11.138949380952093 msec\nrounds: 84"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 597.7649793602925,
            "unit": "iter/sec",
            "range": "stddev: 0.0019746316118686522",
            "extra": "mean: 1.6728982702703084 msec\nrounds: 592"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 41506.34043130797,
            "unit": "iter/sec",
            "range": "stddev: 0.000005517951190727167",
            "extra": "mean: 24.09270462316418 usec\nrounds: 16958"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 12.627302957121914,
            "unit": "iter/sec",
            "range": "stddev: 0.0005402398432435287",
            "extra": "mean: 79.19347491666784 msec\nrounds: 12"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 44.01858489132727,
            "unit": "iter/sec",
            "range": "stddev: 0.00020907869490369288",
            "extra": "mean: 22.717677146341526 msec\nrounds: 41"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 9.600678063423963,
            "unit": "iter/sec",
            "range": "stddev: 0.011165042706157422",
            "extra": "mean: 104.15930972727173 msec\nrounds: 11"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 18.821566796208593,
            "unit": "iter/sec",
            "range": "stddev: 0.007788277095507597",
            "extra": "mean: 53.13053959999969 msec\nrounds: 20"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_methods",
            "value": 8.3594248630985,
            "unit": "iter/sec",
            "range": "stddev: 0.010202826803726162",
            "extra": "mean: 119.62545466666717 msec\nrounds: 9"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_methods",
            "value": 11.632280669189518,
            "unit": "iter/sec",
            "range": "stddev: 0.0006230906832380923",
            "extra": "mean: 85.96766433333276 msec\nrounds: 12"
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
          "id": "19f62aaff6843f29978156eef6671ea6ad7f9b51",
          "message": "feat(core): infer class method return types in dependency order (OP 0005)\n\nSecond slice of return-type inference: class methods may now omit the\nreturn annotation. Because method forward/mutual calls are legal (all\nsignatures are installed before bodies are checked), naive source-order\ninference would let a method see the Unknown placeholder of a method it\ncalls and silently collapse. Instead methods are inferred in dependency\n(topological) order:\n\n- _method_dependencies scans a method body for same-class method\n  references (this.m(), calls on other instances, method-as-value);\n  matching by attribute name is a conservative, sound approximation.\n- _infer_and_check_methods runs Kahn's algorithm callees-first,\n  backfilling class_type.methods (mutable tuple on the shared ClassType)\n  and the method metadata after each inference, so later methods see\n  concrete return types.\n- Methods on a recursive call cycle (including self-recursion) cannot be\n  ordered and require an explicit annotation, matching the def-slice\n  recursion rule and Kotlin/Scala.\n- Annotated methods and __init__ are checked last so their call sites see\n  inferred types. __init__, the constructor type, definite assignment and\n  slot initializers are unaffected.\n\nReuses the existing infer mode / _ReturnInfer / join_types machinery.\nFlips the method-annotation rejection test, adds forward/backward call,\nself/mutual recursion, annotated-calls-inferred and cross-module class\nexport tests, an astm metadata test, and drops annotations from the\ntest_vm Point differential. Docs synced (design 14, spec 11, impl 09,\nOP 0005/0017, roadmap, conformance 06, CHANGELOG); markdownlint guidance\nadded to AGENTS.md. 1053 tests pass.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-22T05:15:17+08:00",
          "tree_id": "64819bc80233f5f202311849976893c468e9e1cd",
          "url": "https://github.com/fyabc/oort-lang/commit/19f62aaff6843f29978156eef6671ea6ad7f9b51"
        },
        "date": 1795295843155,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 32.11664103338102,
            "unit": "iter/sec",
            "range": "stddev: 0.00024639060737659816",
            "extra": "mean: 31.136506428571767 msec\nrounds: 7"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 3.2974406131209246,
            "unit": "iter/sec",
            "range": "stddev: 0.015608006843153761",
            "extra": "mean: 303.26550720000114 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 59.10718905502833,
            "unit": "iter/sec",
            "range": "stddev: 0.00019191336500487934",
            "extra": "mean: 16.918415779661046 msec\nrounds: 59"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 53.90331647811131,
            "unit": "iter/sec",
            "range": "stddev: 0.00027973391079247025",
            "extra": "mean: 18.551734203702907 msec\nrounds: 54"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 51.91897369208544,
            "unit": "iter/sec",
            "range": "stddev: 0.00016405457785231104",
            "extra": "mean: 19.260781346154396 msec\nrounds: 52"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 206.11295022388413,
            "unit": "iter/sec",
            "range": "stddev: 0.0000814617078049367",
            "extra": "mean: 4.8517087301587765 msec\nrounds: 189"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 60.89788004857746,
            "unit": "iter/sec",
            "range": "stddev: 0.00006032301465854783",
            "extra": "mean: 16.420932866666504 msec\nrounds: 60"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 91.31286942230784,
            "unit": "iter/sec",
            "range": "stddev: 0.00006885562503632523",
            "extra": "mean: 10.951358842696699 msec\nrounds: 89"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 116.1743749230391,
            "unit": "iter/sec",
            "range": "stddev: 0.00016516223635940078",
            "extra": "mean: 8.607750208791398 msec\nrounds: 91"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 205.75436915520464,
            "unit": "iter/sec",
            "range": "stddev: 0.0011336637582925778",
            "extra": "mean: 4.860164107842978 msec\nrounds: 204"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 102.69921848884812,
            "unit": "iter/sec",
            "range": "stddev: 0.0007137047576310711",
            "extra": "mean: 9.737172441176735 msec\nrounds: 102"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 59899.319255930764,
            "unit": "iter/sec",
            "range": "stddev: 0.00000255343139683685",
            "extra": "mean: 16.69468054765894 usec\nrounds: 26367"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 69163.4158297039,
            "unit": "iter/sec",
            "range": "stddev: 8.704875370632609e-7",
            "extra": "mean: 14.458510876071072 usec\nrounds: 26756"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 107339.75551317605,
            "unit": "iter/sec",
            "range": "stddev: 8.041640978054191e-7",
            "extra": "mean: 9.316212760306215 usec\nrounds: 18730"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 69300.2971121095,
            "unit": "iter/sec",
            "range": "stddev: 0.000005973460721110595",
            "extra": "mean: 14.429952564016649 usec\nrounds: 18467"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 153214.74767613588,
            "unit": "iter/sec",
            "range": "stddev: 6.844780974716187e-7",
            "extra": "mean: 6.526786847659026 usec\nrounds: 38822"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 141840.13784980608,
            "unit": "iter/sec",
            "range": "stddev: 0.000001599620190560704",
            "extra": "mean: 7.050190553670329 usec\nrounds: 37496"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 66985.79691640758,
            "unit": "iter/sec",
            "range": "stddev: 0.0000049058893754114336",
            "extra": "mean: 14.928537780149318 usec\nrounds: 16821"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 60201.70593975605,
            "unit": "iter/sec",
            "range": "stddev: 0.000005261054571497598",
            "extra": "mean: 16.610824965669604 usec\nrounds: 16751"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 8652.62599294474,
            "unit": "iter/sec",
            "range": "stddev: 0.000020417986951928293",
            "extra": "mean: 115.57185076708382 usec\nrounds: 5019"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 2723.710008540654,
            "unit": "iter/sec",
            "range": "stddev: 0.00008937843550208232",
            "extra": "mean: 367.14628094192506 usec\nrounds: 1826"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program_vm",
            "value": 2230.416890501283,
            "unit": "iter/sec",
            "range": "stddev: 0.0006410276668389125",
            "extra": "mean: 448.3466764705371 usec\nrounds: 1530"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 13350.07034770079,
            "unit": "iter/sec",
            "range": "stddev: 0.0002998510043724761",
            "extra": "mean: 74.90597232487427 usec\nrounds: 15429"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_empty",
            "value": 166091.88264428757,
            "unit": "iter/sec",
            "range": "stddev: 7.718886292974775e-7",
            "extra": "mean: 6.020763833122781 usec\nrounds: 31880"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_fib",
            "value": 22959.498950821995,
            "unit": "iter/sec",
            "range": "stddev: 0.0000020013548490562705",
            "extra": "mean: 43.55495745538463 usec\nrounds: 7451"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_empty",
            "value": 172809.159494363,
            "unit": "iter/sec",
            "range": "stddev: 6.434542928656496e-7",
            "extra": "mean: 5.786730303682888 usec\nrounds: 25855"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_fib",
            "value": 27925.776187521755,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017944674826812742",
            "extra": "mean: 35.8092105760998 usec\nrounds: 12689"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 157.84237032668662,
            "unit": "iter/sec",
            "range": "stddev: 0.0025420830340011436",
            "extra": "mean: 6.3354345093164675 msec\nrounds: 161"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 117.46527987332595,
            "unit": "iter/sec",
            "range": "stddev: 0.0018021124346479561",
            "extra": "mean: 8.513153853448403 msec\nrounds: 116"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 1264.0559308254112,
            "unit": "iter/sec",
            "range": "stddev: 0.00002500533671423918",
            "extra": "mean: 791.1042348790797 usec\nrounds: 992"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 372.6600260175434,
            "unit": "iter/sec",
            "range": "stddev: 0.0032565001942691644",
            "extra": "mean: 2.683410964912357 msec\nrounds: 456"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 172.69966372720728,
            "unit": "iter/sec",
            "range": "stddev: 0.001338354898635732",
            "extra": "mean: 5.790399230768502 msec\nrounds: 169"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 1263.322726289507,
            "unit": "iter/sec",
            "range": "stddev: 0.000939605672221799",
            "extra": "mean: 791.5633742591573 usec\nrounds: 1181"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 95659.38786765015,
            "unit": "iter/sec",
            "range": "stddev: 8.967986846455479e-7",
            "extra": "mean: 10.453757046653417 usec\nrounds: 28808"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 26.595923313266603,
            "unit": "iter/sec",
            "range": "stddev: 0.0006714271637752267",
            "extra": "mean: 37.59974745833242 msec\nrounds: 24"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 77.60073961287354,
            "unit": "iter/sec",
            "range": "stddev: 0.0003372793455846043",
            "extra": "mean: 12.886475115942135 msec\nrounds: 69"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 19.49320670100672,
            "unit": "iter/sec",
            "range": "stddev: 0.006729735150878881",
            "extra": "mean: 51.299922857143635 msec\nrounds: 21"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 32.78906102662885,
            "unit": "iter/sec",
            "range": "stddev: 0.00421185305441403",
            "extra": "mean: 30.49797611428622 msec\nrounds: 35"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_methods",
            "value": 20.182856856112398,
            "unit": "iter/sec",
            "range": "stddev: 0.004227109717787323",
            "extra": "mean: 49.54699957142831 msec\nrounds: 21"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_methods",
            "value": 19.568185350239546,
            "unit": "iter/sec",
            "range": "stddev: 0.00482934464419931",
            "extra": "mean: 51.10335895238025 msec\nrounds: 21"
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
          "id": "3dabb5588dc8caf5b8328db9fb215d59ebc87626",
          "message": "docs(spec): add formal HIR/bytecode/VM spec (spec 12), wrap up backend\n\nElevate the type-erased backend's behavior from design 13 + opcodes.py +\ndifferential tests into a normative spec, docs/spec/12-hir-bytecode-vm.md.\nThis closes the 'formal spec pending' item design 13 reserved until the\ndefault backend and optimization direction stabilized (both now true:\ndefault is VM, Python micro-optimization frozen). Generic ADT does not\naffect this spec: ADT lowering uses only constructor names + arities, and\ntype parameters are erased before HIR.\n\nThe spec covers the execution targets, HIR instruction set, scopes /\nregisters / frame-capture closures and the cell protocol, the scratch\nwindow calling convention, 32-bit ABC/ABx/AsBx/Ax encoding with the opcode\ntable and constant-pool descriptors, VM semantics, structural validation,\nthe three-tier explicit rejections (with the VM-vs-interpreter timing\ndifference), and differential consistency anchored by tests/unit/backend.\nImplementation details (caches, hot-path inlining) are deliberately left\nout; typed IR/VM is scoped out to design 02.\n\nAlso corrects the stale '-t eval is still the default' statements in\ndesign 13/02 and spec index/11 (default is now VM), registers spec 12 in\nmkdocs nav + spec index, and cross-links design 00-INDEX/02/13. mkdocs\nstrict and markdownlint pass; backend tests unchanged (153 pass).\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-22T05:55:53+08:00",
          "tree_id": "13eabee988f5aaf883a3ef4cb626f367cc5da7ca",
          "url": "https://github.com/fyabc/oort-lang/commit/3dabb5588dc8caf5b8328db9fb215d59ebc87626"
        },
        "date": 1795298226165,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 28.974860814698122,
            "unit": "iter/sec",
            "range": "stddev: 0.0020633681776790363",
            "extra": "mean: 34.51267657143425 msec\nrounds: 7"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 3.1691878173745214,
            "unit": "iter/sec",
            "range": "stddev: 0.016329450806004422",
            "extra": "mean: 315.5382570000029 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 57.023026104647734,
            "unit": "iter/sec",
            "range": "stddev: 0.0003510128288340155",
            "extra": "mean: 17.536775375000552 msec\nrounds: 56"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 52.10314409973795,
            "unit": "iter/sec",
            "range": "stddev: 0.00029123819336627057",
            "extra": "mean: 19.192699735850095 msec\nrounds: 53"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 48.963411927225536,
            "unit": "iter/sec",
            "range": "stddev: 0.001462168996653288",
            "extra": "mean: 20.42341333333353 msec\nrounds: 51"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 196.58471673313096,
            "unit": "iter/sec",
            "range": "stddev: 0.00010115971219958487",
            "extra": "mean: 5.086865431952815 msec\nrounds: 169"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 54.732937535331125,
            "unit": "iter/sec",
            "range": "stddev: 0.002375607884222409",
            "extra": "mean: 18.2705340701745 msec\nrounds: 57"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 86.45103128300102,
            "unit": "iter/sec",
            "range": "stddev: 0.00012383617969844124",
            "extra": "mean: 11.5672419999995 msec\nrounds: 84"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 104.51748854211358,
            "unit": "iter/sec",
            "range": "stddev: 0.002357011303833463",
            "extra": "mean: 9.567776780218619 msec\nrounds: 91"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 196.71379813457213,
            "unit": "iter/sec",
            "range": "stddev: 0.0019974644524194465",
            "extra": "mean: 5.0835274875629155 msec\nrounds: 201"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 97.86416719513386,
            "unit": "iter/sec",
            "range": "stddev: 0.0013552829836732867",
            "extra": "mean: 10.218244620690172 msec\nrounds: 87"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 61662.195771553656,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011961482045985868",
            "extra": "mean: 16.21739199338285 usec\nrounds: 20508"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 64649.91939060462,
            "unit": "iter/sec",
            "range": "stddev: 0.000001237810609338154",
            "extra": "mean: 15.467923385304745 usec\nrounds: 18965"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 106843.13541504553,
            "unit": "iter/sec",
            "range": "stddev: 8.370546692573282e-7",
            "extra": "mean: 9.359515668604958 usec\nrounds: 14009"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 70250.52877966533,
            "unit": "iter/sec",
            "range": "stddev: 0.000005991291151940377",
            "extra": "mean: 14.234768298134993 usec\nrounds: 11053"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 155782.40971895502,
            "unit": "iter/sec",
            "range": "stddev: 6.406724978010309e-7",
            "extra": "mean: 6.419209985287086 usec\nrounds: 29664"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 148382.99827269043,
            "unit": "iter/sec",
            "range": "stddev: 8.257543898054378e-7",
            "extra": "mean: 6.739316576972335 usec\nrounds: 24130"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 63822.791408462734,
            "unit": "iter/sec",
            "range": "stddev: 0.000012570655030112572",
            "extra": "mean: 15.668383941405022 usec\nrounds: 11757"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 57699.37659680694,
            "unit": "iter/sec",
            "range": "stddev: 0.000005772068331089213",
            "extra": "mean: 17.33120978044223 usec\nrounds: 11431"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 8633.692860041489,
            "unit": "iter/sec",
            "range": "stddev: 0.000020182755915458813",
            "extra": "mean: 115.82529239929374 usec\nrounds: 3355"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 2651.7056142384554,
            "unit": "iter/sec",
            "range": "stddev: 0.00010031497024902919",
            "extra": "mean: 377.1157682928504 usec\nrounds: 1312"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program_vm",
            "value": 2039.9237588684123,
            "unit": "iter/sec",
            "range": "stddev: 0.0010433250902093822",
            "extra": "mean: 490.21439926496106 usec\nrounds: 1633"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 11918.730861383969,
            "unit": "iter/sec",
            "range": "stddev: 0.0007545483718187563",
            "extra": "mean: 83.90155056189286 usec\nrounds: 14151"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_empty",
            "value": 167237.33215794273,
            "unit": "iter/sec",
            "range": "stddev: 5.65605375053199e-7",
            "extra": "mean: 5.97952614465039 usec\nrounds: 21840"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_fib",
            "value": 21453.716891884407,
            "unit": "iter/sec",
            "range": "stddev: 0.000017103805745942808",
            "extra": "mean: 46.61196961997218 usec\nrounds: 5135"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_empty",
            "value": 171769.5158310982,
            "unit": "iter/sec",
            "range": "stddev: 6.271750016682379e-7",
            "extra": "mean: 5.821754780885015 usec\nrounds: 25414"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_fib",
            "value": 27631.067151690095,
            "unit": "iter/sec",
            "range": "stddev: 0.000003882351624855588",
            "extra": "mean: 36.19114652757209 usec\nrounds: 8524"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 153.64387530218315,
            "unit": "iter/sec",
            "range": "stddev: 0.004465941848816493",
            "extra": "mean: 6.508557520000219 msec\nrounds: 150"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 115.46306716294106,
            "unit": "iter/sec",
            "range": "stddev: 0.0006077659935086473",
            "extra": "mean: 8.660778070175493 msec\nrounds: 114"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 1195.7038729502258,
            "unit": "iter/sec",
            "range": "stddev: 0.001147106501509552",
            "extra": "mean: 836.3274742371162 usec\nrounds: 1048"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 225.80152882995026,
            "unit": "iter/sec",
            "range": "stddev: 0.009145359000078583",
            "extra": "mean: 4.428667977501135 msec\nrounds: 400"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 167.8171798422294,
            "unit": "iter/sec",
            "range": "stddev: 0.0031690072205869334",
            "extra": "mean: 5.958865480519538 msec\nrounds: 154"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 1082.669624164597,
            "unit": "iter/sec",
            "range": "stddev: 0.00271228731719158",
            "extra": "mean: 923.6427971012984 usec\nrounds: 1035"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 86374.28325416803,
            "unit": "iter/sec",
            "range": "stddev: 0.000009500166165089913",
            "extra": "mean: 11.577520094231804 usec\nrounds: 23763"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 25.206611498243262,
            "unit": "iter/sec",
            "range": "stddev: 0.0029026234510235163",
            "extra": "mean: 39.67213126086756 msec\nrounds: 23"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 73.22419888713613,
            "unit": "iter/sec",
            "range": "stddev: 0.0010022207722142323",
            "extra": "mean: 13.656687477610328 msec\nrounds: 67"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 18.590261752573777,
            "unit": "iter/sec",
            "range": "stddev: 0.011106374859444101",
            "extra": "mean: 53.79160408333424 msec\nrounds: 12"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 30.071620898456555,
            "unit": "iter/sec",
            "range": "stddev: 0.012675437691096083",
            "extra": "mean: 33.25394408823921 msec\nrounds: 34"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_methods",
            "value": 18.770575859457725,
            "unit": "iter/sec",
            "range": "stddev: 0.010186329725006727",
            "extra": "mean: 53.27487059999498 msec\nrounds: 20"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_methods",
            "value": 19.201800817297677,
            "unit": "iter/sec",
            "range": "stddev: 0.00921708280118072",
            "extra": "mean: 52.078448761907985 msec\nrounds: 21"
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
          "id": "8056c816fa8fbcf9f1f76d0683df4b95ef3169e0",
          "message": "docs(design 14): explain why join does not merge to Object\n\nAdd a subsection to the type-lattice section answering a natural question:\nwhy if c { 1 } else { \"s\" } errors instead of inferring Object. The static\nmodel has no top type and no subtyping, so LUB reduces to equality; an\nObject value would be unusable (no downcast/type-test) and only defer the\nerror; it aligns with the explicit-over-implicit stance; and the idiomatic\nstatic expression of 'Int or String' is a sum type/ADT, not Object. Notes\nthe cross-language pattern (Rust/Haskell error, TypeScript infers a union\nbecause it has union types).\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-22T06:24:38+08:00",
          "tree_id": "03460a3ee686e4691525acffba72e3f115fffb1a",
          "url": "https://github.com/fyabc/oort-lang/commit/8056c816fa8fbcf9f1f76d0683df4b95ef3169e0"
        },
        "date": 1795299931510,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 18.463258396434785,
            "unit": "iter/sec",
            "range": "stddev: 0.00029703675585101696",
            "extra": "mean: 54.16162079999367 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 1.573158522615868,
            "unit": "iter/sec",
            "range": "stddev: 0.004843895380737963",
            "extra": "mean: 635.6638480000015 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 25.978946012674793,
            "unit": "iter/sec",
            "range": "stddev: 0.0004715516125900732",
            "extra": "mean: 38.49270865385043 msec\nrounds: 26"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 21.93986273893812,
            "unit": "iter/sec",
            "range": "stddev: 0.0007720631880658863",
            "extra": "mean: 45.579136565208955 msec\nrounds: 23"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 21.02779618116153,
            "unit": "iter/sec",
            "range": "stddev: 0.00039619776175955034",
            "extra": "mean: 47.556101047616394 msec\nrounds: 21"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 95.71568091452744,
            "unit": "iter/sec",
            "range": "stddev: 0.0017176957471202847",
            "extra": "mean: 10.447608902171254 msec\nrounds: 92"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 24.649357295017907,
            "unit": "iter/sec",
            "range": "stddev: 0.0005615457669782521",
            "extra": "mean: 40.56900908333697 msec\nrounds: 24"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 38.62487607626178,
            "unit": "iter/sec",
            "range": "stddev: 0.0002711994384244326",
            "extra": "mean: 25.89005070270203 msec\nrounds: 37"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 64.16462640264805,
            "unit": "iter/sec",
            "range": "stddev: 0.0004562393381767628",
            "extra": "mean: 15.584911127273864 msec\nrounds: 55"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 98.22784085205937,
            "unit": "iter/sec",
            "range": "stddev: 0.0018422374146176252",
            "extra": "mean: 10.180413122447604 msec\nrounds: 98"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 43.68398323433496,
            "unit": "iter/sec",
            "range": "stddev: 0.0002416313479415593",
            "extra": "mean: 22.891685372088844 msec\nrounds: 43"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 31450.227213369682,
            "unit": "iter/sec",
            "range": "stddev: 0.00000250305410309623",
            "extra": "mean: 31.79627266968977 usec\nrounds: 15847"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 31582.03279142587,
            "unit": "iter/sec",
            "range": "stddev: 0.0000026802305050024418",
            "extra": "mean: 31.6635729753117 usec\nrounds: 14779"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 42549.87167680979,
            "unit": "iter/sec",
            "range": "stddev: 0.0000026710706308972397",
            "extra": "mean: 23.50183350952413 usec\nrounds: 13238"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 27665.52067629452,
            "unit": "iter/sec",
            "range": "stddev: 0.000009603486688462785",
            "extra": "mean: 36.14607553209219 usec\nrounds: 11558"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 73772.16230073215,
            "unit": "iter/sec",
            "range": "stddev: 0.000001548892501470869",
            "extra": "mean: 13.555248603443408 usec\nrounds: 24706"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 70505.20471850873,
            "unit": "iter/sec",
            "range": "stddev: 0.0000017034601710540726",
            "extra": "mean: 14.183350066033979 usec\nrounds: 21256"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 28080.595462509078,
            "unit": "iter/sec",
            "range": "stddev: 0.000008693405478551219",
            "extra": "mean: 35.61178043161936 usec\nrounds: 9965"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 23880.100541811662,
            "unit": "iter/sec",
            "range": "stddev: 0.000008688228441954381",
            "extra": "mean: 41.87587059146172 usec\nrounds: 9157"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 4098.745943344723,
            "unit": "iter/sec",
            "range": "stddev: 0.000037313271933303776",
            "extra": "mean: 243.97706367327672 usec\nrounds: 2450"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1322.5007036650316,
            "unit": "iter/sec",
            "range": "stddev: 0.0007646613575243208",
            "extra": "mean: 756.1432649742349 usec\nrounds: 985"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program_vm",
            "value": 1172.2086751586444,
            "unit": "iter/sec",
            "range": "stddev: 0.000188193835085077",
            "extra": "mean: 853.0904276618343 usec\nrounds: 1099"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 6896.379262093882,
            "unit": "iter/sec",
            "range": "stddev: 0.0005782739550238571",
            "extra": "mean: 145.00362610515413 usec\nrounds: 9048"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_empty",
            "value": 84149.17395075355,
            "unit": "iter/sec",
            "range": "stddev: 0.000001531647793937084",
            "extra": "mean: 11.883657949931012 usec\nrounds: 23289"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_fib",
            "value": 10310.132916644356,
            "unit": "iter/sec",
            "range": "stddev: 0.000006746400933093292",
            "extra": "mean: 96.99196005374783 usec\nrounds: 4456"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_empty",
            "value": 84770.71392705364,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013438249690027878",
            "extra": "mean: 11.796526815387134 usec\nrounds: 26123"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_fib",
            "value": 12967.180878543142,
            "unit": "iter/sec",
            "range": "stddev: 0.000008688069980178701",
            "extra": "mean: 77.11776440588602 usec\nrounds: 7254"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 79.06540242032895,
            "unit": "iter/sec",
            "range": "stddev: 0.002921592040071049",
            "extra": "mean: 12.647757038961005 msec\nrounds: 77"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 54.909641024180885,
            "unit": "iter/sec",
            "range": "stddev: 0.0002788643731912123",
            "extra": "mean: 18.21173807272978 msec\nrounds: 55"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 617.4575200310893,
            "unit": "iter/sec",
            "range": "stddev: 0.00006349574274117172",
            "extra": "mean: 1.6195446124773887 msec\nrounds: 529"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 180.5768498885735,
            "unit": "iter/sec",
            "range": "stddev: 0.00601603122336199",
            "extra": "mean: 5.537808421273594 msec\nrounds: 235"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 87.64575152073444,
            "unit": "iter/sec",
            "range": "stddev: 0.0027957566421718282",
            "extra": "mean: 11.409566152940442 msec\nrounds: 85"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 584.1593603929657,
            "unit": "iter/sec",
            "range": "stddev: 0.001973934541040136",
            "extra": "mean: 1.7118616387954428 msec\nrounds: 598"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 43364.37182682336,
            "unit": "iter/sec",
            "range": "stddev: 0.000002496181557691882",
            "extra": "mean: 23.060405532761404 usec\nrounds: 18869"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 12.555695889869332,
            "unit": "iter/sec",
            "range": "stddev: 0.0012226125107956105",
            "extra": "mean: 79.64512750001045 msec\nrounds: 12"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 42.44118607352269,
            "unit": "iter/sec",
            "range": "stddev: 0.00039080639670380544",
            "extra": "mean: 23.562018230773692 msec\nrounds: 39"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 9.758101056203826,
            "unit": "iter/sec",
            "range": "stddev: 0.008144810252556622",
            "extra": "mean: 102.47895510000262 msec\nrounds: 10"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 18.14253332973812,
            "unit": "iter/sec",
            "range": "stddev: 0.007556815397996106",
            "extra": "mean: 55.11909400000174 msec\nrounds: 19"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_methods",
            "value": 8.408930946167937,
            "unit": "iter/sec",
            "range": "stddev: 0.008598750947426927",
            "extra": "mean: 118.92118111110348 msec\nrounds: 9"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_methods",
            "value": 11.061684877325453,
            "unit": "iter/sec",
            "range": "stddev: 0.0013475077589779323",
            "extra": "mean: 90.4021413636387 msec\nrounds: 11"
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
          "id": "8b5475aa6917bfd9035bec2404d7909b1a2d2a3c",
          "message": "chore(rust): commit Cargo.lock for the oort-vm spike binary\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-22T07:10:50+08:00",
          "tree_id": "42527345d4f058f7823491dcb7a09cb33ccc74d5",
          "url": "https://github.com/fyabc/oort-lang/commit/8b5475aa6917bfd9035bec2404d7909b1a2d2a3c"
        },
        "date": 1795302698945,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 24.623366525877852,
            "unit": "iter/sec",
            "range": "stddev: 0.0016405225223135457",
            "extra": "mean: 40.611830999999654 msec\nrounds: 6"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.3494323628096323,
            "unit": "iter/sec",
            "range": "stddev: 0.002024012111199825",
            "extra": "mean: 425.63472599999557 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 40.316152463032466,
            "unit": "iter/sec",
            "range": "stddev: 0.00016820898768622167",
            "extra": "mean: 24.803954219513905 msec\nrounds: 41"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 36.87810591145543,
            "unit": "iter/sec",
            "range": "stddev: 0.00037320663197553837",
            "extra": "mean: 27.116360108108765 msec\nrounds: 37"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 35.24042461058525,
            "unit": "iter/sec",
            "range": "stddev: 0.00011221745965470713",
            "extra": "mean: 28.376502583332314 msec\nrounds: 36"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 137.90904047422163,
            "unit": "iter/sec",
            "range": "stddev: 0.00012528216485122536",
            "extra": "mean: 7.25115624444449 msec\nrounds: 135"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 40.903982482369095,
            "unit": "iter/sec",
            "range": "stddev: 0.0007297279235494427",
            "extra": "mean: 24.447497268292434 msec\nrounds: 41"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 60.81536631152281,
            "unit": "iter/sec",
            "range": "stddev: 0.0008132329941852076",
            "extra": "mean: 16.44321263934454 msec\nrounds: 61"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 95.17125635144235,
            "unit": "iter/sec",
            "range": "stddev: 0.00013879003009183158",
            "extra": "mean: 10.507374162502003 msec\nrounds: 80"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 136.04564752712315,
            "unit": "iter/sec",
            "range": "stddev: 0.001461525997807509",
            "extra": "mean: 7.350474037036958 msec\nrounds: 135"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 70.4031841099248,
            "unit": "iter/sec",
            "range": "stddev: 0.00007831277821183986",
            "extra": "mean: 14.203903028570965 msec\nrounds: 70"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 42095.649692164705,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015437249022502847",
            "extra": "mean: 23.755423833882073 usec\nrounds: 19359"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 45543.30717545356,
            "unit": "iter/sec",
            "range": "stddev: 0.000001631405329558579",
            "extra": "mean: 21.957123055371113 usec\nrounds: 18577"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 72868.58872988627,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012044139360813433",
            "extra": "mean: 13.723334257328094 usec\nrounds: 16233"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 51189.18311031637,
            "unit": "iter/sec",
            "range": "stddev: 0.000008150013318905596",
            "extra": "mean: 19.53537718789003 usec\nrounds: 13826"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 99023.26167865327,
            "unit": "iter/sec",
            "range": "stddev: 9.016982143175567e-7",
            "extra": "mean: 10.098637260052733 usec\nrounds: 17139"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 93283.37493418684,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010176456866381605",
            "extra": "mean: 10.72002380601601 usec\nrounds: 27052"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 47622.58957587772,
            "unit": "iter/sec",
            "range": "stddev: 0.000005489410440345926",
            "extra": "mean: 20.998438113212774 usec\nrounds: 12232"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 42578.45550976066,
            "unit": "iter/sec",
            "range": "stddev: 0.000006375958817729176",
            "extra": "mean: 23.486056223217414 usec\nrounds: 11650"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 6577.519980825646,
            "unit": "iter/sec",
            "range": "stddev: 0.00041716097177863735",
            "extra": "mean: 152.03298551963877 usec\nrounds: 2348"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1912.8007036767183,
            "unit": "iter/sec",
            "range": "stddev: 0.0001307528748900584",
            "extra": "mean: 522.7936177971052 usec\nrounds: 1371"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program_vm",
            "value": 1560.7250822468698,
            "unit": "iter/sec",
            "range": "stddev: 0.000829295680962681",
            "extra": "mean: 640.7278330917628 usec\nrounds: 1378"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 9301.636091865663,
            "unit": "iter/sec",
            "range": "stddev: 0.0004457681235736377",
            "extra": "mean: 107.50796850400394 usec\nrounds: 11557"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_empty",
            "value": 109699.99091579353,
            "unit": "iter/sec",
            "range": "stddev: 7.878781806237105e-7",
            "extra": "mean: 9.115771037461679 usec\nrounds: 22353"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_fib",
            "value": 15039.485954964015,
            "unit": "iter/sec",
            "range": "stddev: 0.0000031342423383649637",
            "extra": "mean: 66.49163428820081 usec\nrounds: 4818"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_empty",
            "value": 114145.92630843465,
            "unit": "iter/sec",
            "range": "stddev: 9.87429729214496e-7",
            "extra": "mean: 8.760715623769979 usec\nrounds: 26799"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_fib",
            "value": 18211.799979268533,
            "unit": "iter/sec",
            "range": "stddev: 0.0000022801696082793045",
            "extra": "mean: 54.90945437234944 usec\nrounds: 8931"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 109.43616681662094,
            "unit": "iter/sec",
            "range": "stddev: 0.002292659539694713",
            "extra": "mean: 9.1377469541278 msec\nrounds: 109"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 78.30254668823764,
            "unit": "iter/sec",
            "range": "stddev: 0.0022686858656883724",
            "extra": "mean: 12.770976708861205 msec\nrounds: 79"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 863.6320812746369,
            "unit": "iter/sec",
            "range": "stddev: 0.000056879923232444076",
            "extra": "mean: 1.1579004783195377 msec\nrounds: 738"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 237.3781698433509,
            "unit": "iter/sec",
            "range": "stddev: 0.004999316558633001",
            "extra": "mean: 4.21268729411771 msec\nrounds: 306"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 120.70572647882197,
            "unit": "iter/sec",
            "range": "stddev: 0.00008515513659021662",
            "extra": "mean: 8.28461108823575 msec\nrounds: 34"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 751.5203610590056,
            "unit": "iter/sec",
            "range": "stddev: 0.0015865834376850231",
            "extra": "mean: 1.330635937249723 msec\nrounds: 749"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 65189.84771166437,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011375843880884104",
            "extra": "mean: 15.339811874128229 usec\nrounds: 18275"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 19.787135840822554,
            "unit": "iter/sec",
            "range": "stddev: 0.00047454789258665587",
            "extra": "mean: 50.537885222221725 msec\nrounds: 18"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 49.87221359432764,
            "unit": "iter/sec",
            "range": "stddev: 0.0007934440330806796",
            "extra": "mean: 20.051245531915548 msec\nrounds: 47"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 12.970165500025184,
            "unit": "iter/sec",
            "range": "stddev: 0.009127042621049178",
            "extra": "mean: 77.10001849999973 msec\nrounds: 14"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 20.91082498677768,
            "unit": "iter/sec",
            "range": "stddev: 0.006647932205019652",
            "extra": "mean: 47.822120869564905 msec\nrounds: 23"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_methods",
            "value": 13.782343145254393,
            "unit": "iter/sec",
            "range": "stddev: 0.00030910955029559605",
            "extra": "mean: 72.55660300000041 msec\nrounds: 14"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_methods",
            "value": 12.882437273575224,
            "unit": "iter/sec",
            "range": "stddev: 0.0007307231823585459",
            "extra": "mean: 77.6250626153814 msec\nrounds: 13"
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
          "id": "a69ea231f1fc877c441a9cc91a71ff07dcc9d848",
          "message": "benchmarks: add the Rust VM spike to the cross-language reference (RESULTS)\n\nRegister oort-rust as a reference runtime so RESULTS.md's cross-language\ntable includes the Rust spike alongside the Python backends and host\nlanguages. oort_rust.py wraps the Rust VM for the runner: it compiles .ort\nto .obc (mtime-cached, frontend imported only when compiling so cached runs\nstay fast) and executes rust/target/release/oort-vm, forwarding output.\n\nRESULTS now shows Oort Rust VM (spike): fib 5.37ms / loop 1.10ms /\nmethods 1.91ms exec, ~60-117x faster than the Python VM and in the CPython\nballpark. The spike is kept separate from the official Oort-vs-CPython\nsummary (which still uses only oort/oort-vm). Documented caveat: oort-rust\nstartup includes the Python wrapper overhead, not a pure native startup;\nexec_ms is the fair comparison. reference README + report.py maintenance\nrules updated to require the full runtime set including oort-rust.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-22T07:33:47+08:00",
          "tree_id": "f817aef64c5d4856d709e63b4a7f14a9be6eaa0e",
          "url": "https://github.com/fyabc/oort-lang/commit/a69ea231f1fc877c441a9cc91a71ff07dcc9d848"
        },
        "date": 1795304077431,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 25.43762627263897,
            "unit": "iter/sec",
            "range": "stddev: 0.0002376559065376438",
            "extra": "mean: 39.31184416667103 msec\nrounds: 6"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.3439619996430414,
            "unit": "iter/sec",
            "range": "stddev: 0.0017183837192939221",
            "extra": "mean: 426.628076800003 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 39.64594285880308,
            "unit": "iter/sec",
            "range": "stddev: 0.0003787088842462194",
            "extra": "mean: 25.223261899999372 msec\nrounds: 40"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 36.82720703919063,
            "unit": "iter/sec",
            "range": "stddev: 0.00021308017400783588",
            "extra": "mean: 27.15383762162099 msec\nrounds: 37"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 35.08870994310684,
            "unit": "iter/sec",
            "range": "stddev: 0.0001949920544290284",
            "extra": "mean: 28.49919537142885 msec\nrounds: 35"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 136.9463233265827,
            "unit": "iter/sec",
            "range": "stddev: 0.00009937007378259755",
            "extra": "mean: 7.302131051851975 msec\nrounds: 135"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 40.568291261903155,
            "unit": "iter/sec",
            "range": "stddev: 0.0005118731412843004",
            "extra": "mean: 24.649793444445105 msec\nrounds: 36"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 60.5692452553286,
            "unit": "iter/sec",
            "range": "stddev: 0.0005315549980511779",
            "extra": "mean: 16.510029071429194 msec\nrounds: 56"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 93.10850066173239,
            "unit": "iter/sec",
            "range": "stddev: 0.0002918598134750771",
            "extra": "mean: 10.74015791139251 msec\nrounds: 79"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 134.91624519038743,
            "unit": "iter/sec",
            "range": "stddev: 0.00153565453195574",
            "extra": "mean: 7.412005860293898 msec\nrounds: 136"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 69.63862547175992,
            "unit": "iter/sec",
            "range": "stddev: 0.00013003901133874486",
            "extra": "mean: 14.35984689855091 msec\nrounds: 69"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 42551.13935384128,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015626902352182227",
            "extra": "mean: 23.501133346496996 usec\nrounds: 20263"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 46907.748811714446,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014124168570147548",
            "extra": "mean: 21.318439390770042 usec\nrounds: 19568"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 71957.11378265006,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015351483229177912",
            "extra": "mean: 13.897166623727408 usec\nrounds: 15556"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 50637.58056909689,
            "unit": "iter/sec",
            "range": "stddev: 0.000008451466527337936",
            "extra": "mean: 19.748178897201896 usec\nrounds: 14472"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 101326.93405122626,
            "unit": "iter/sec",
            "range": "stddev: 9.807905192602236e-7",
            "extra": "mean: 9.869044290775104 usec\nrounds: 30232"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 93375.97250272935,
            "unit": "iter/sec",
            "range": "stddev: 0.0000036358956851450105",
            "extra": "mean: 10.709393146837325 usec\nrounds: 26995"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 47646.333571908035,
            "unit": "iter/sec",
            "range": "stddev: 0.0000054045922889573385",
            "extra": "mean: 20.987973785869503 usec\nrounds: 12169"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 42024.983614371544,
            "unit": "iter/sec",
            "range": "stddev: 0.000007093370402934679",
            "extra": "mean: 23.795369182678844 usec\nrounds: 11539"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 6892.025865608874,
            "unit": "iter/sec",
            "range": "stddev: 0.00003080193619273776",
            "extra": "mean: 145.095218662772 usec\nrounds: 2154"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1850.6900874183273,
            "unit": "iter/sec",
            "range": "stddev: 0.000641560487124633",
            "extra": "mean: 540.3389831708552 usec\nrounds: 1129"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program_vm",
            "value": 1548.6754790090745,
            "unit": "iter/sec",
            "range": "stddev: 0.0008684351019110486",
            "extra": "mean: 645.713071301325 usec\nrounds: 1122"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 9260.013777049498,
            "unit": "iter/sec",
            "range": "stddev: 0.0004384456656203376",
            "extra": "mean: 107.99120002158661 usec\nrounds: 9284"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_empty",
            "value": 108082.93300277126,
            "unit": "iter/sec",
            "range": "stddev: 7.916760405044218e-7",
            "extra": "mean: 9.252154546679076 usec\nrounds: 21741"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_fib",
            "value": 14839.475023857645,
            "unit": "iter/sec",
            "range": "stddev: 0.000009595808844900971",
            "extra": "mean: 67.38782863897039 usec\nrounds: 5077"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_empty",
            "value": 115765.48237999874,
            "unit": "iter/sec",
            "range": "stddev: 8.997424373804794e-7",
            "extra": "mean: 8.638153441260778 usec\nrounds: 27737"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_fib",
            "value": 18448.12313541686,
            "unit": "iter/sec",
            "range": "stddev: 0.000002317929885991794",
            "extra": "mean: 54.20605622911263 usec\nrounds: 9817"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 109.44078567833633,
            "unit": "iter/sec",
            "range": "stddev: 0.0025581396211167293",
            "extra": "mean: 9.137361302751948 msec\nrounds: 109"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 79.15762372644956,
            "unit": "iter/sec",
            "range": "stddev: 0.0024334900019760417",
            "extra": "mean: 12.633021974683938 msec\nrounds: 79"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 860.3447425642394,
            "unit": "iter/sec",
            "range": "stddev: 0.0000911959693584675",
            "extra": "mean: 1.1623247641631669 msec\nrounds: 759"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 237.47473508146314,
            "unit": "iter/sec",
            "range": "stddev: 0.005083900870576657",
            "extra": "mean: 4.210974273355693 msec\nrounds: 289"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 121.2414880923667,
            "unit": "iter/sec",
            "range": "stddev: 0.00006577978537692933",
            "extra": "mean: 8.248001700854738 msec\nrounds: 117"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 781.0239550170903,
            "unit": "iter/sec",
            "range": "stddev: 0.001625724862222488",
            "extra": "mean: 1.2803704592877923 msec\nrounds: 786"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 65212.414547302455,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012129457381947176",
            "extra": "mean: 15.334503513508773 usec\nrounds: 25473"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 19.38992433993499,
            "unit": "iter/sec",
            "range": "stddev: 0.0003099603862038144",
            "extra": "mean: 51.573176999996114 msec\nrounds: 18"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 59.824780549024126,
            "unit": "iter/sec",
            "range": "stddev: 0.00012691650270953004",
            "extra": "mean: 16.715481290909846 msec\nrounds: 55"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 12.955892596479643,
            "unit": "iter/sec",
            "range": "stddev: 0.008684966116038974",
            "extra": "mean: 77.18495599999946 msec\nrounds: 14"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 23.76388359461697,
            "unit": "iter/sec",
            "range": "stddev: 0.01008868196046695",
            "extra": "mean: 42.08066396296107 msec\nrounds: 27"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_methods",
            "value": 13.392997414859831,
            "unit": "iter/sec",
            "range": "stddev: 0.006981445335102191",
            "extra": "mean: 74.66588464285654 msec\nrounds: 14"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_methods",
            "value": 15.485048820496978,
            "unit": "iter/sec",
            "range": "stddev: 0.006978800469943791",
            "extra": "mean: 64.57842087500154 msec\nrounds: 16"
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
          "id": "6ded4733db7fcebc5ce602591fee38052d693e37",
          "message": "docs(benchmarks): record 0.5.0 results\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-22T20:55:13+08:00",
          "tree_id": "9dd24458c1f1cc99d66e46077800facd35d4b19b",
          "url": "https://github.com/fyabc/oort-lang/commit/6ded4733db7fcebc5ce602591fee38052d693e37"
        },
        "date": 1795352551337,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 24.227663281609686,
            "unit": "iter/sec",
            "range": "stddev: 0.000740634029732961",
            "extra": "mean: 41.27513200000029 msec\nrounds: 6"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.776356736600251,
            "unit": "iter/sec",
            "range": "stddev: 0.002211157390926532",
            "extra": "mean: 360.18426119999845 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 48.42616474046948,
            "unit": "iter/sec",
            "range": "stddev: 0.00013287543282155146",
            "extra": "mean: 20.649993765959035 msec\nrounds: 47"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 44.515127344247546,
            "unit": "iter/sec",
            "range": "stddev: 0.0002024343264291498",
            "extra": "mean: 22.464273599999586 msec\nrounds: 45"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 42.19168683271349,
            "unit": "iter/sec",
            "range": "stddev: 0.00033398221419187005",
            "extra": "mean: 23.701351499998477 msec\nrounds: 42"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 167.58696388640647,
            "unit": "iter/sec",
            "range": "stddev: 0.00009985516349119119",
            "extra": "mean: 5.967051236024648 msec\nrounds: 161"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 48.97946703905179,
            "unit": "iter/sec",
            "range": "stddev: 0.0002331490700723815",
            "extra": "mean: 20.41671868750002 msec\nrounds: 48"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 73.12249449199973,
            "unit": "iter/sec",
            "range": "stddev: 0.000179465747619376",
            "extra": "mean: 13.675682250000499 msec\nrounds: 72"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 92.79039307161203,
            "unit": "iter/sec",
            "range": "stddev: 0.00024763863892708084",
            "extra": "mean: 10.77697773333322 msec\nrounds: 75"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 160.13065428993355,
            "unit": "iter/sec",
            "range": "stddev: 0.00325324352180393",
            "extra": "mean: 6.244900481012173 msec\nrounds: 158"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 83.15029404355757,
            "unit": "iter/sec",
            "range": "stddev: 0.00015073854429653613",
            "extra": "mean: 12.026415679013217 msec\nrounds: 81"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 49390.62859242804,
            "unit": "iter/sec",
            "range": "stddev: 0.0000019788842122061307",
            "extra": "mean: 20.24675588261915 usec\nrounds: 12367"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 56294.81385171839,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014206686928953663",
            "extra": "mean: 17.76362566246367 usec\nrounds: 14340"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 87955.22165613767,
            "unit": "iter/sec",
            "range": "stddev: 0.0000013493757765076895",
            "extra": "mean: 11.36942163490322 usec\nrounds: 10668"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 58384.62704252582,
            "unit": "iter/sec",
            "range": "stddev: 0.000008335778212278754",
            "extra": "mean: 17.1277963165137 usec\nrounds: 9176"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 125864.85619875992,
            "unit": "iter/sec",
            "range": "stddev: 9.066801827594987e-7",
            "extra": "mean: 7.945029535654071 usec\nrounds: 23023"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 119939.32127206396,
            "unit": "iter/sec",
            "range": "stddev: 0.0000010295585093568133",
            "extra": "mean: 8.337549265696222 usec\nrounds: 20156"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 56009.59219959819,
            "unit": "iter/sec",
            "range": "stddev: 0.000005800609784906964",
            "extra": "mean: 17.85408464386523 usec\nrounds: 9983"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 49274.22641573859,
            "unit": "iter/sec",
            "range": "stddev: 0.0000061164256035441",
            "extra": "mean: 20.294585480911614 usec\nrounds: 8265"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 6909.4414062132455,
            "unit": "iter/sec",
            "range": "stddev: 0.00002667568147166519",
            "extra": "mean: 144.72949999992184 usec\nrounds: 2778"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 2143.007474101946,
            "unit": "iter/sec",
            "range": "stddev: 0.00012575730650256795",
            "extra": "mean: 466.63393015885885 usec\nrounds: 1260"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program_vm",
            "value": 1654.357927077238,
            "unit": "iter/sec",
            "range": "stddev: 0.0018315015450583996",
            "extra": "mean: 604.464114828346 usec\nrounds: 1106"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 9773.45574306101,
            "unit": "iter/sec",
            "range": "stddev: 0.000985849726093627",
            "extra": "mean: 102.31795449731108 usec\nrounds: 13208"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_empty",
            "value": 136046.96939114816,
            "unit": "iter/sec",
            "range": "stddev: 7.627423639671653e-7",
            "extra": "mean: 7.350402618120095 usec\nrounds: 18181"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_fib",
            "value": 18485.555366231813,
            "unit": "iter/sec",
            "range": "stddev: 0.0000030134529814471208",
            "extra": "mean: 54.09629195272833 usec\nrounds: 3641"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_empty",
            "value": 140133.10213696535,
            "unit": "iter/sec",
            "range": "stddev: 9.150880722506022e-7",
            "extra": "mean: 7.136072667702777 usec\nrounds: 19541"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_fib",
            "value": 22881.005372751613,
            "unit": "iter/sec",
            "range": "stddev: 0.0000023650624233565744",
            "extra": "mean: 43.70437328732389 usec\nrounds: 8101"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 125.65856752377994,
            "unit": "iter/sec",
            "range": "stddev: 0.005518393046135793",
            "extra": "mean: 7.958072574802808 msec\nrounds: 127"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 92.19831971955531,
            "unit": "iter/sec",
            "range": "stddev: 0.005260480515159333",
            "extra": "mean: 10.846184648936713 msec\nrounds: 94"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 1038.061085147534,
            "unit": "iter/sec",
            "range": "stddev: 0.00003217482413755995",
            "extra": "mean: 963.3344456389824 usec\nrounds: 837"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 237.31568284198045,
            "unit": "iter/sec",
            "range": "stddev: 0.008605430951358505",
            "extra": "mean: 4.213796526316647 msec\nrounds: 19"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 138.75418385932815,
            "unit": "iter/sec",
            "range": "stddev: 0.00366895680759349",
            "extra": "mean: 7.206989888058587 msec\nrounds: 134"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 840.6187931896943,
            "unit": "iter/sec",
            "range": "stddev: 0.003719596317110631",
            "extra": "mean: 1.1895998615561996 msec\nrounds: 874"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 78230.9686376922,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012068400956554806",
            "extra": "mean: 12.782661616159427 usec\nrounds: 19998"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 20.52794111167233,
            "unit": "iter/sec",
            "range": "stddev: 0.0004809952374766362",
            "extra": "mean: 48.714091421053084 msec\nrounds: 19"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 64.32120956235231,
            "unit": "iter/sec",
            "range": "stddev: 0.00041401867017781054",
            "extra": "mean: 15.546971314813513 msec\nrounds: 54"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 14.765796924226416,
            "unit": "iter/sec",
            "range": "stddev: 0.017505118567654986",
            "extra": "mean: 67.72407917647088 msec\nrounds: 17"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 26.018375252028065,
            "unit": "iter/sec",
            "range": "stddev: 0.017618164446061093",
            "extra": "mean: 38.43437533333495 msec\nrounds: 30"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_methods",
            "value": 15.617699844973732,
            "unit": "iter/sec",
            "range": "stddev: 0.0125585047401868",
            "extra": "mean: 64.02991541176478 msec\nrounds: 17"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_methods",
            "value": 19.026006591331356,
            "unit": "iter/sec",
            "range": "stddev: 0.0016385265394623272",
            "extra": "mean: 52.55963700000087 msec\nrounds: 18"
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
          "id": "879acb37fd51cad97915d4016e38314585196d25",
          "message": "docs: fix backend drift and publish performance roadmap\n\n- implementation/index.md: replace the stale \"only tree-walking\n  interpreter\" claim with the two-path model (VM default, eval fallback),\n  link spec 12 / design 13, and state the type-erasure boundary.\n- roadmap.md: add the staged performance roadmap (Rust VM v2, typed IR,\n  native compilation) with per-stage gates; point stage 3 backends at it.\n\nCo-Authored-By: Claude Code <noreply@anthropic.com>",
          "timestamp": "2026-11-22T21:30:29+08:00",
          "tree_id": "4a97014eb54e0fbb0f34e08035b75af161932bb3",
          "url": "https://github.com/fyabc/oort-lang/commit/879acb37fd51cad97915d4016e38314585196d25"
        },
        "date": 1795354557851,
        "tool": "pytest",
        "benches": [
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[10-55]",
            "value": 24.549975222528897,
            "unit": "iter/sec",
            "range": "stddev: 0.0001487594491296599",
            "extra": "mean: 40.73323866666575 msec\nrounds: 6"
          },
          {
            "name": "benchmarks/test_ast_interpreter.py::test_recursion[20-6765]",
            "value": 2.3392735190429734,
            "unit": "iter/sec",
            "range": "stddev: 0.001419216001427723",
            "extra": "mean: 427.48314460000074 msec\nrounds: 5"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_member_call",
            "value": 39.756300556645165,
            "unit": "iter/sec",
            "range": "stddev: 0.00010600881226955593",
            "extra": "mean: 25.15324580000069 msec\nrounds: 40"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_method_call",
            "value": 36.36218548563492,
            "unit": "iter/sec",
            "range": "stddev: 0.00014739132509097457",
            "extra": "mean: 27.501097270268737 msec\nrounds: 37"
          },
          {
            "name": "benchmarks/test_extensions.py::test_extension_operator_call",
            "value": 34.29414682728568,
            "unit": "iter/sec",
            "range": "stddev: 0.0026846162158492607",
            "extra": "mean: 29.159494914285588 msec\nrounds: 35"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_builtin_loop",
            "value": 137.6869593680391,
            "unit": "iter/sec",
            "range": "stddev: 0.0001933243931948754",
            "extra": "mean: 7.262851940298764 msec\nrounds: 134"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_user_closure",
            "value": 40.33848616718045,
            "unit": "iter/sec",
            "range": "stddev: 0.0003285108810823509",
            "extra": "mean: 24.790221325003614 msec\nrounds: 40"
          },
          {
            "name": "benchmarks/test_iterators.py::test_iterator_infinite_break",
            "value": 60.43360008167138,
            "unit": "iter/sec",
            "range": "stddev: 0.0002412973310359835",
            "extra": "mean: 16.547086366666502 msec\nrounds: 60"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_fibonacci",
            "value": 93.16807416208523,
            "unit": "iter/sec",
            "range": "stddev: 0.000315854139047894",
            "extra": "mean: 10.733290443036228 msec\nrounds: 79"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_loop",
            "value": 134.96721531077154,
            "unit": "iter/sec",
            "range": "stddev: 0.0015699217397904788",
            "extra": "mean: 7.409206729926445 msec\nrounds: 137"
          },
          {
            "name": "benchmarks/test_macro.py::test_macro_method_dispatch",
            "value": 69.02453511611826,
            "unit": "iter/sec",
            "range": "stddev: 0.00010728362215900983",
            "extra": "mean: 14.48760210145168 msec\nrounds: 69"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_arithmetic",
            "value": 41473.5175618131,
            "unit": "iter/sec",
            "range": "stddev: 0.0000016722985989514777",
            "extra": "mean: 24.111772012334775 usec\nrounds: 18944"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_variable_lookup",
            "value": 46276.75086343313,
            "unit": "iter/sec",
            "range": "stddev: 0.0000015382881966410651",
            "extra": "mean: 21.60912296870388 usec\nrounds: 16492"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_function_call",
            "value": 71127.11031198544,
            "unit": "iter/sec",
            "range": "stddev: 0.0000014368214929497846",
            "extra": "mean: 14.059336807213054 usec\nrounds: 11802"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_attribute",
            "value": 49592.47202210788,
            "unit": "iter/sec",
            "range": "stddev: 0.000007332272918834574",
            "extra": "mean: 20.16435074166516 usec\nrounds: 13212"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_index",
            "value": 102992.7538819583,
            "unit": "iter/sec",
            "range": "stddev: 9.908588218226786e-7",
            "extra": "mean: 9.709420928254007 usec\nrounds: 28784"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_dict",
            "value": 95770.8584796155,
            "unit": "iter/sec",
            "range": "stddev: 0.0000011819338891051696",
            "extra": "mean: 10.441589601213051 usec\nrounds: 26099"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_closure",
            "value": 47294.72157882968,
            "unit": "iter/sec",
            "range": "stddev: 0.000007619678453444326",
            "extra": "mean: 21.144008604284192 usec\nrounds: 11506"
          },
          {
            "name": "benchmarks/test_micro.py::test_micro_class_instantiation",
            "value": 39268.09001688409,
            "unit": "iter/sec",
            "range": "stddev: 0.00020748164455951912",
            "extra": "mean: 25.46596994073382 usec\nrounds: 11311"
          },
          {
            "name": "benchmarks/test_startup.py::test_compiler_construction",
            "value": 6827.188384303866,
            "unit": "iter/sec",
            "range": "stddev: 0.000030389469201737687",
            "extra": "mean: 146.47318100948593 usec\nrounds: 3149"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program",
            "value": 1901.7181350568546,
            "unit": "iter/sec",
            "range": "stddev: 0.00012936107329897012",
            "extra": "mean: 525.8402817776692 usec\nrounds: 1125"
          },
          {
            "name": "benchmarks/test_startup.py::test_empty_program_vm",
            "value": 1551.2750560473398,
            "unit": "iter/sec",
            "range": "stddev: 0.0007737462169968957",
            "extra": "mean: 644.6310060241717 usec\nrounds: 1328"
          },
          {
            "name": "benchmarks/test_startup.py::test_runtime_construction",
            "value": 9194.666033291409,
            "unit": "iter/sec",
            "range": "stddev: 0.00047018506538330394",
            "extra": "mean: 108.7587081879069 usec\nrounds: 11737"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_empty",
            "value": 110055.77946371399,
            "unit": "iter/sec",
            "range": "stddev: 7.825318355368802e-7",
            "extra": "mean: 9.086301554292346 usec\nrounds: 24125"
          },
          {
            "name": "benchmarks/test_startup.py::test_hir_lowering_fib",
            "value": 14951.74723735089,
            "unit": "iter/sec",
            "range": "stddev: 0.000003874564879955501",
            "extra": "mean: 66.88181549122933 usec\nrounds: 3886"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_empty",
            "value": 115837.41194142333,
            "unit": "iter/sec",
            "range": "stddev: 7.837061326785057e-7",
            "extra": "mean: 8.632789555982828 usec\nrounds: 25584"
          },
          {
            "name": "benchmarks/test_startup.py::test_bytecode_compile_fib",
            "value": 18201.056265659423,
            "unit": "iter/sec",
            "range": "stddev: 0.000002428258357178026",
            "extra": "mean: 54.941866307327196 usec\nrounds: 7233"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_map",
            "value": 108.81116245064666,
            "unit": "iter/sec",
            "range": "stddev: 0.002647137883459564",
            "extra": "mean: 9.190233588889088 msec\nrounds: 90"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_filter",
            "value": 80.45948525817079,
            "unit": "iter/sec",
            "range": "stddev: 0.00023209672235760428",
            "extra": "mean: 12.42861543037834 msec\nrounds: 79"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_sorted",
            "value": 846.0713535843778,
            "unit": "iter/sec",
            "range": "stddev: 0.0009172068281146267",
            "extra": "mean: 1.1819334099464591 msec\nrounds: 744"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_zip_enumerate",
            "value": 236.64121506052862,
            "unit": "iter/sec",
            "range": "stddev: 0.005027294535598874",
            "extra": "mean: 4.225806564356161 msec\nrounds: 303"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_stdlib_string_join",
            "value": 118.85614045084989,
            "unit": "iter/sec",
            "range": "stddev: 0.0022274081277426903",
            "extra": "mean: 8.413532495727692 msec\nrounds: 117"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_list_equality_projection",
            "value": 750.6349214872232,
            "unit": "iter/sec",
            "range": "stddev: 0.001842784263197898",
            "extra": "mean: 1.3322055387707157 msec\nrounds: 748"
          },
          {
            "name": "benchmarks/test_stdlib.py::test_host_len_does_not_project",
            "value": 66002.42563345168,
            "unit": "iter/sec",
            "range": "stddev: 0.0000012744898831319354",
            "extra": "mean: 15.150958323161609 usec\nrounds: 24546"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_fib",
            "value": 18.7712313772297,
            "unit": "iter/sec",
            "range": "stddev: 0.0008042583954619868",
            "extra": "mean: 53.273010166666126 msec\nrounds: 18"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_fib",
            "value": 53.37564640256658,
            "unit": "iter/sec",
            "range": "stddev: 0.0005594773475237118",
            "extra": "mean: 18.735136104167438 msec\nrounds: 48"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_loop",
            "value": 13.342742166091547,
            "unit": "iter/sec",
            "range": "stddev: 0.007209245205910829",
            "extra": "mean: 74.94711263636202 msec\nrounds: 11"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_loop",
            "value": 23.244765705536672,
            "unit": "iter/sec",
            "range": "stddev: 0.008539307133305599",
            "extra": "mean: 43.02043792000063 msec\nrounds: 25"
          },
          {
            "name": "benchmarks/test_vm.py::test_interpreter_methods",
            "value": 13.496383072969024,
            "unit": "iter/sec",
            "range": "stddev: 0.007673822141648171",
            "extra": "mean: 74.09392535714484 msec\nrounds: 14"
          },
          {
            "name": "benchmarks/test_vm.py::test_vm_methods",
            "value": 14.706731248538855,
            "unit": "iter/sec",
            "range": "stddev: 0.006391131468261089",
            "extra": "mean: 67.99607493333042 msec\nrounds: 15"
          }
        ]
      }
    ]
  }
}