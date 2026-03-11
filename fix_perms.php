<?php
header("Content-Type: text/plain; charset=utf-8");
echo "=== Fix permissions ===\n\n";
$base = "/home/tumxxzse/lmdmanagerpro/";

function fix_perms_recursive($dir) {
    $count = 0;
    if (!is_dir($dir)) {
        echo "NOT FOUND: $dir\n";
        return 0;
    }
    chmod($dir, 0755);
    $count++;
    $items = new RecursiveIteratorIterator(
        new RecursiveDirectoryIterator($dir, RecursiveDirectoryIterator::SKIP_DOTS),
        RecursiveIteratorIterator::SELF_FIRST
    );
    foreach ($items as $item) {
        if ($item->isDir()) {
            chmod($item->getPathname(), 0755);
        } else {
            chmod($item->getPathname(), 0644);
        }
        $count++;
    }
    return $count;
}

// Fix core/static
$n = fix_perms_recursive($base . "core/static");
echo "core/static: $n items fixed\n";

// Fix reglage/static if exists
$n = fix_perms_recursive($base . "reglage/static");
echo "reglage/static: $n items fixed\n";

// Fix static/ root if exists
$n = fix_perms_recursive($base . "static");
echo "static/: $n items fixed\n";

// Fix staticfiles/
$n = fix_perms_recursive($base . "staticfiles");
echo "staticfiles/: $n items fixed\n";

// Fix media/
$n = fix_perms_recursive($base . "media");
echo "media/: $n items fixed\n";

echo "\nDone! Now run: manage.py collectstatic --noinput\n";
?>
