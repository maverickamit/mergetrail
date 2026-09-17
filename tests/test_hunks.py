from mergetrail.git import hunk_id, parse_hunks

PATCH = """\
diff --git a/app.py b/app.py
index 1234567..89abcde 100644
--- a/app.py
+++ b/app.py
@@ -1,4 +1,4 @@
 \"\"\"Fixture module.\"\"\"
 
-GREETING = "hello"
+GREETING = "hi there"
 
@@ -34 +34 @@ FILLER_30 = 30
-FAREWELL = "bye"
+FAREWELL = "farewell"
"""


def test_parse_hunks_reads_both_hunks():
    hunks = parse_hunks("app.py", PATCH)

    assert len(hunks) == 2
    assert hunks[0].header.startswith("@@ -1,4 +1,4 @@")
    assert hunks[0].old_start == 1
    assert hunks[0].old_lines == 4
    assert '+GREETING = "hi there"' in hunks[0].body


def test_parse_hunks_defaults_a_missing_line_count_to_one():
    single_line = parse_hunks("app.py", PATCH)[1]

    assert single_line.old_start == 34
    assert single_line.old_lines == 1
    assert single_line.new_lines == 1


def test_parse_hunks_drops_the_file_preamble():
    body = "\n".join(hunk.body for hunk in parse_hunks("app.py", PATCH))

    assert "diff --git" not in body
    assert "index 1234567" not in body


def test_parse_hunks_stops_at_the_next_file():
    two_files = PATCH + "diff --git a/other.py b/other.py\n@@ -1 +1 @@\n-a\n+b\n"

    assert len(parse_hunks("app.py", two_files)) == 2


def test_hunk_id_is_stable():
    first = parse_hunks("app.py", PATCH)
    second = parse_hunks("app.py", PATCH)

    assert [hunk.id for hunk in first] == [hunk.id for hunk in second]
    assert first[0].id != first[1].id


def test_hunk_id_is_scoped_to_the_path():
    header, body = "@@ -1 +1 @@", "-a\n+b"

    assert hunk_id("app.py", header, body) != hunk_id("other.py", header, body)
