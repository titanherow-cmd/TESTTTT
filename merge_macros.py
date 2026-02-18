# Whitelist Feature + Random Queue Verification - v3.22.0

## What's Fixed/New

### ✅ 1. WORKING WHITELIST
Previous whitelist didn't work - ALL folders were processed anyway. Now it actually works!

### ✅ 2. PARENT FOLDER SUPPORT  
List "Desktop" once → includes ALL Desktop subfolders automatically

### ✅ 3. CONFIRMED RANDOM QUEUE
Files are shuffled randomly - NOT sequential (1,2,3,4,5,6...)

## How Whitelist Works

### Create the File
File name: **"specific folders to include for merge.txt"**

Location: **Root directory** (same place as `input_macros` folder)

```
your_project/
├── input_macros/                              # Your macros
├── chat inserts/                              # Chat files
├── specific folders to include for merge.txt  # ← CREATE HERE
└── output/                                    # Output
```

### Two Ways to Use It

#### Method 1: Parent Folder (Easiest!)
```text
# Process ALL Desktop folders
Desktop
```
This includes ALL subfolders under Desktop automatically!

#### Method 2: Specific Folders
```text
# Process only these specific folders
1-Mining
23-Fishing  
45-Woodcutting
```

#### Method 3: Mix Both
```text
# All Desktop folders + some specific Mobile folders
Desktop
5-Mobile Mining
12-Mobile Fishing
```

## File Format

- **One folder name per line**
- **Case-insensitive** ("desktop" = "Desktop" = "DESKTOP")
- **Lines starting with #** are comments (ignored)
- **Empty lines** are ignored
- **No file = process ALL folders** (backward compatible)

## Examples

### Example 1: All Desktop Only
```text
Desktop
```
Result: Processes Desktop/1-Mining, Desktop/2-Combat, Desktop/3-Fishing... (all Desktop subfolders)

### Example 2: Specific Folders
```text
1-Mining
23-Fishing
45-Combat
```
Result: Only processes these 3 specific folders

### Example 3: Mixed
```text
# All Desktop folders
Desktop

# Plus these specific Mobile folders
5-Mobile Mining
12-Mobile Combat
```

## How the Random Queue Works

### CONFIRMED: Files are TRULY Random

Every time you run the script, files in each folder are:
1. **Shuffled randomly** (NOT 1,2,3,4,5,6...)
2. **No file used twice** until all files are used once
3. **Then reshuffled** and the cycle repeats

### Example:
**Folder has files:** 1.json, 2.json, 3.json, 4.json, 5.json, 6.json

**Run 1 might use:** 4, 1, 6, 2, 5, 3  
**Run 2 might use:** 2, 5, 1, 4, 6, 3  
**Run 3 might use:** 6, 3, 2, 1, 5, 4

It's **NOT** always 1→2→3→4→5→6!

### Code Evidence
From `QueueFileSelector.__init__()` lines 782-784:
```python
self.eff_pool = list(self.efficient)
self.ineff_pool = list(self.inefficient)
self.rng.shuffle(self.eff_pool)  # ← RANDOMIZED HERE
self.rng.shuffle(self.ineff_pool)  # ← RANDOMIZED HERE
```

And when pool empties, line 800:
```python
self.eff_pool = list(self.efficient)
self.rng.shuffle(self.eff_pool)  # ← RESHUFFLED RANDOMLY AGAIN
```

## Console Output

When using whitelist, you'll see:

```
✓ Loaded whitelist from: /path/to/specific folders to include for merge.txt
  Including ALL subfolders under:
    - desktop/* (all subfolders)

============================================================
WHITELIST FILTER SUMMARY
============================================================
✓ Processed folders: 8
    - 1-Mining
    - 2-Combat
    - 3-Fishing
    - 4-Woodcutting
    - 5-Crafting
    - 6-Smithing
    - 7-Herblore
    - 8-Agility

⊘ Skipped folders: 45
    - 10-Old Test
    - 11-Broken Macro
    ... and 43 more
============================================================
```

## Troubleshooting

### "All folders still processing" (whitelist not working)
1. Check filename: Must be exactly `specific folders to include for merge.txt`
2. Check location: Must be in root directory (same level as `input_macros`)
3. Check folder names: Must match exactly (case-insensitive)
4. Check file isn't empty: At least one folder name required

### "Parent folder not including subfolders"
- Make sure you typed exactly: `Desktop` or `Mobile` (case-insensitive)
- These are the only parent folders supported currently

### "Files seem to be in same order every time"
- The queue IS random! You might be seeing a pattern by chance
- Try running 3-5 times and compare - orders will be different

## Use Cases

### 1. Process Only Desktop Folders
```text
Desktop
```

### 2. Process Only Mobile Folders
```text
Mobile
```

### 3. Process Specific Activities
```text
1-Mining
2-Mining Iron
3-Mining Mithril
23-Fishing Lobsters
45-Combat Sand Crabs
```

### 4. Test New Recordings
```text
78-New Combat Macro
79-New Mining Spot
80-New Fishing Method
```

### 5. Process Everything (Remove File)
Delete the whitelist file → all folders processed

## Technical Details

- **Matching**: Case-insensitive string comparison
- **Performance**: Negligible impact (O(1) lookups)
- **Backward Compatible**: No file = process all folders
- **Z+100**: Still works! Z+100 files added to matching folders (if folder is whitelisted)
- **Random Seed**: Uses Python's `random.Random()` - truly random every run

## Summary

✅ Whitelist **actually works** now  
✅ Parent folders (Desktop/Mobile) include **ALL subfolders**  
✅ Queue is **truly random** - NOT sequential  
✅ **Easy to use** - just list folder names  
✅ **Backward compatible** - no file = all folders  

Copy/paste folder names, run script, done!
