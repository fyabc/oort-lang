window.BENCHMARK_DATA = {
  "lastUpdate": 1795113967116,
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
      }
    ]
  }
}