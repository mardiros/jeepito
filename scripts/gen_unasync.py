from pathlib import Path

import unasync

unasync.unasync_files(
    [str(p) for p in Path("src/messagebus/service/_async").iterdir() if p.is_file()],
    rules=[
        unasync.Rule(
            "src/messagebus/service/_async",
            "src/messagebus/service/_sync",
            additional_replacements={
                "_async": "_sync",
            },
        ),
    ],
)

unasync.unasync_files(
    [str(p) for p in Path("tests/_async").iterdir() if p.is_file()],
    rules=[
        unasync.Rule(
            "tests/_async",
            "tests/_sync",
            additional_replacements={
                "_async": "_sync",
                "AsyncSleep": "SyncSleep",
            },
        ),
    ],
)
