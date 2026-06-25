#!/usr/bin/env node
// Generates Lucide-backed wrapper .svelte files for src/lib/components/icons/
// preserving the existing API (className, strokeWidth) and import paths.
// Existing custom icons with no clean Lucide equivalent are left untouched.
const fs = require('fs');
const path = require('path');

const ICONS_DIR = path.join(__dirname, '..', 'src', 'lib', 'components', 'icons');

// Map: existing PascalCase wrapper name -> Lucide kebab-case icon name.
// `null` = no clean Lucide equivalent; leave the existing custom file untouched.
const MAP = {
  AdjustmentsHorizontal: 'sliders-horizontal',
  AdjustmentsHorizontalOutline: 'sliders-horizontal',
  Agile: 'workflow',
  AlignHorizontal: 'align-horizontal-justify-center',
  AlignVertical: 'align-vertical-justify-center',
  AppNotification: 'bell',
  ArchiveBox: 'archive',
  ArrowDownTray: 'download',
  ArrowForward: 'arrow-right',
  ArrowLeft: 'arrow-left',
  ArrowLeftTag: 'arrow-left-from-line',
  ArrowPath: 'refresh-cw',
  ArrowRight: 'arrow-right',
  ArrowRightCircle: 'arrow-right-circle',
  ArrowRightTag: 'arrow-right-to-line',
  ArrowsPointingOut: 'maximize',
  ArrowTurnDownRight: 'corner-down-right',
  ArrowUpCircle: 'arrow-up-circle',
  ArrowUpLeft: 'arrow-up-left',
  ArrowUpLeftAlt: 'arrow-up-left',
  ArrowUpTray: 'upload',
  ArrowUturnLeft: 'undo-2',
  ArrowUturnRight: 'redo-2',
  Bars3BottomLeft: 'panel-bottom',
  BarsArrowUp: 'arrow-up-from-line',
  Bold: 'bold',
  Bolt: 'zap',
  Bookmark: 'bookmark',
  BookmarkSlash: 'bookmark-x',
  BookOpen: 'book-open',
  Calendar: 'calendar',
  CalendarSolid: 'calendar',
  Camera: 'camera',
  CameraSolid: 'camera',
  ChartBar: 'bar-chart-3',
  ChatBubble: 'message-circle',
  ChatBubbleDotted: 'message-circle-more',
  ChatBubbleDottedChecked: 'message-circle-check',
  ChatBubbleOval: 'message-circle',
  ChatBubbles: 'messages-square',
  ChatCheck: 'message-square-check',
  ChatPlus: 'message-square-plus',
  Check: 'check',
  CheckBox: 'check-square',
  CheckCircle: 'circle-check-big',
  ChevronDown: 'chevron-down',
  ChevronLeft: 'chevron-left',
  ChevronRight: 'chevron-right',
  ChevronUp: 'chevron-up',
  ChevronUpDown: 'chevrons-up-down',
  Clip: 'paperclip',
  Clipboard: 'clipboard',
  ClockRotateRight: 'history',
  Cloud: 'cloud',
  CloudArrowUp: 'cloud-upload',
  Code: 'square-code',
  CodeBracket: 'code',
  Cog6: 'settings',
  Cog6Solid: 'settings',
  Collapse: 'minimize-2',
  CommandLine: 'terminal',
  CommandLineSolid: 'terminal-square',
  Component: 'component',
  Computer: 'monitor',
  Cube: 'box',
  CursorArrowRays: 'mouse-pointer-click',
  Database: 'database',
  DatabaseSettings: 'database',
  Document: 'file-text',
  DocumentArrowDown: 'file-down',
  DocumentArrowUp: 'file-up',
  DocumentArrowUpSolid: 'file-up',
  DocumentChartBar: 'file-bar-chart',
  DocumentCheck: 'file-check',
  DocumentDuplicate: 'files',
  DocumentPage: 'file',
  Download: 'download',
  EditPencil: 'pencil',
  EllipsisHorizontal: 'ellipsis',
  EllipsisVertical: 'ellipsis-vertical',
  Expand: 'maximize',
  Eye: 'eye',
  EyeSlash: 'eye-off',
  Face: 'smile',
  FaceId: 'scan-face',
  FaceSmile: 'smile',
  FilePlusAlt: 'file-plus-2',
  FloppyDisk: 'save',
  Folder: 'folder',
  FolderOpen: 'folder-open',
  GarbageBin: 'trash-2',
  Github: null,
  Glasses: 'glasses',
  GlobeAlt: 'globe',
  GlobeAltSolid: 'globe',
  Grid: 'layout-grid',
  H1: 'heading-1',
  H2: 'heading-2',
  H3: 'heading-3',
  Hashtag: 'hash',
  Headphone: 'headphones',
  Heart: 'heart',
  Home: 'house',
  Info: 'info',
  InfoCircle: 'info',
  Italic: 'italic',
  Keyboard: 'keyboard',
  KeyframePlus: 'key-round',
  Keyframes: 'key-round',
  Knobs: 'sliders-vertical',
  Label: 'tag',
  Lifebuoy: 'life-buoy',
  LightBulb: 'lightbulb',
  LineSpace: 'align-justify',
  LineSpaceSmaller: 'align-justify',
  Link: 'link',
  LinkSlash: 'link-2-off',
  ListBullet: 'list',
  Lock: 'lock',
  LockClosed: 'lock',
  Map: 'map',
  MenuLines: 'menu',
  Merge: 'git-merge',
  Mic: 'mic',
  MicSolid: 'mic',
  Minus: 'minus',
  NewFolderAlt: 'folder-plus',
  Note: 'file-text',
  NumberedList: 'list-ordered',
  PageEdit: 'file-pen-line',
  PagePlus: 'file-plus-2',
  PenAlt: 'pen',
  Pencil: 'pencil',
  PencilSolid: 'pencil',
  PencilSquare: 'square-pen',
  PeopleTag: 'users',
  Photo: 'image',
  PhotoSolid: 'image',
  Pin: 'pin',
  PinSlash: 'pin-off',
  Plus: 'plus',
  PlusAlt: 'plus-circle',
  QuestionMarkCircle: 'circle-help',
  QueueList: 'list',
  Refresh: 'refresh-cw',
  Reset: 'rotate-ccw',
  Search: 'search',
  Settings: 'settings',
  SettingsAlt: 'settings-2',
  Share: 'share-2',
  Sidebar: 'panel-left',
  SignOut: 'log-out',
  SoundHigh: 'volume-2',
  Sparkles: 'sparkles',
  SparklesSolid: 'sparkles',
  Star: 'star',
  Strikethrough: 'strikethrough',
  Tag: 'tag',
  TaskList: 'list-checks',
  Terminal: 'terminal',
  Underline: 'underline',
  Union: 'group',
  User: 'user',
  UserAlt: 'user-round',
  UserBadgeCheck: 'badge-check',
  UserCircle: 'circle-user',
  UserCircleSolid: 'circle-user-round',
  UserGroup: 'users',
  UserPlusSolid: 'user-plus',
  Users: 'users',
  UsersSolid: 'users',
  Voice: 'audio-lines',
  Wrench: 'wrench',
  WrenchAlt: 'wrench',
  WrenchSolid: 'wrench',
  XMark: 'x',
  Youtube: null,
  ZoomReset: 'locate-fixed'
};

const available = new Set(
  fs.readdirSync(path.join(__dirname, '..', 'node_modules', 'lucide-svelte', 'dist', 'icons'))
    .filter(f => f.endsWith('.js'))
    .map(f => f.replace(/\.js$/, ''))
);

let generated = 0;
let skipped = 0;
let missing = [];

for (const [pascal, kebab] of Object.entries(MAP)) {
  if (!kebab) { skipped++; continue; }
  if (!available.has(kebab)) {
    missing.push(`${pascal} -> ${kebab}`);
    continue;
  }
  // PascalCase import name for the Lucide component
  const lucideImport = kebab.split('-').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join('');
  const filePath = path.join(ICONS_DIR, `${pascal}.svelte`);

  // Preserve existing className API. Lucide uses `class` and `size`/`strokeWidth`.
  // Map className -> class, default strokeWidth stays 1.5 to match prior look.
  const content = `<script lang="ts">
\timport ${lucideImport} from 'lucide-svelte/icons/${kebab}';
\texport let className = 'size-4';
\texport let strokeWidth = '1.5';
</script>

<${lucideImport}
\taria-hidden="true"
\tclass={className}
\tstrokeWidth={strokeWidth}
\tsize={undefined}
/>
`;
  fs.writeFileSync(filePath, content);
  generated++;
}

console.log(`Generated ${generated} wrappers, skipped ${skipped} custom.`);
if (missing.length) {
  console.log('Missing Lucide icons (names not found in installed set):');
  missing.forEach(m => console.log('  ' + m));
}