# KALIDIA名簿 - CLAUDE.md

## プロジェクト概要

バドミントンサークル「KALIDIA」の**出欠名簿票**をWebアプリ化したもの。
スマホのChromeで動作し、タップで出席○を付けられる。データは `localStorage` に自動保存。
単一HTMLファイル（index.html）で完結するバニラJS製。ビルド不要、ブラウザで開くだけで動く。

姉妹アプリ「KALIDIAコート割」と同じ構成・同じメンバーリストを共有する。

**公開先:**
- GitHub: https://github.com/sasukewebjob-ai/kalidia-meibo （public）
- GitHub Pages: https://sasukewebjob-ai.github.io/kalidia-meibo/

---

## ファイル構成

```
KALIDIA名簿/
├── index.html          # アプリ本体（HTML/CSS/JS全込み）
├── manifest.json       # PWAマニフェスト（アプリ名・アイコン・theme_color）
├── service-worker.js   # オフラインキャッシュ（Network First戦略）
├── icon-192.png        # PWAアイコン（Android maskable / iOS apple-touch-icon兼用）
├── icon-512.png        # PWAアイコン（大）
├── make_icons.py       # アイコン生成スクリプト（Pillow）
├── members.txt         # メンバーリスト（編集はここだけ）
├── update_members.py   # members.txt → index.html を同期するスクリプト
├── CLAUDE.md           # このファイル
└── README.md           # GitHub公開用の説明
```

---

## メンバーの更新手順

**名簿の原本は `バドミントン系/members.txt`（フリガナ付き・全アプリ共有）に移行した（2026-07-06）。**

1. `バドミントン系/members.txt` を編集（追加・削除・名前変更）
2. バドミントン系フォルダで以下を実行（3アプリへ一括反映）：
   ```
   python update_members.py
   ```
3. `index.html` をブラウザで開き直す

このフォルダ内の `members.txt` は原本から自動生成されるコピーなので直接編集しない。
（このフォルダの `update_members.py` はローカル単体同期用として残置。通常は原本側を使う）

**members.txt の書式：**
```
[男性]
大野
唐澤
...

[女性]
濱島
内田
...
```
`#` で始まる行はコメント。空行は無視される。index.html の RAW 定数を直接編集しない。

---

## 主な機能

| 機能 | 説明 |
|---|---|
| 日付列の追加 | 「＋日付」ボタンで今日の日付で列を追加、自動ソート後にその列へスクロール |
| 日付の自動ソート | 追加・編集・インポート・起動時に古い順→新しい順（左→右）で並び替え |
| 日付編集 | 日付ヘッダーをタップ→モーダルで日付変更・列削除 |
| 出席入力 | セルをタップで ○ ⇔ 空 のトグル |
| 合計行 | 画面下部に bottom sticky で「合計 N/26」を日付列ごとに表示 |
| 自動保存 | `localStorage`（キー: `kalidia_roster_v1`）に即時保存 |
| JSONエクスポート | 全データを .json ファイルでダウンロード |
| JSONインポート | .json ファイルを読み込んで復元 |
| 全リセット | 日付列と出席データを全削除（メンバーは残る） |
| スマホ最適化 | 氏名列 sticky-left、日付ヘッダー sticky-top、合計行 sticky-bottom、44px セル |
| PWA対応 | manifest.json + Service Worker。ホーム画面に追加でアプリ風起動・オフライン動作 |
| バックアップ警告 | 最終JSON保存から 7日経過で起動時に警告モーダル。「あとで」で 3日スヌーズ |

---

## データ構造（localStorage）

```js
{
    version: 1,
    dates: [
        { id: "d_1714000000000", label: "2026-04-20" }
    ],
    attendance: {
        "M_大野|d_1714000000000": true
        // キー形式: "<memberId>|<dateId>"
        // 値が true で出席、未定義で空
    },
    lastBackupAt: "2026-05-26T10:30:00.000Z",   // JSONエクスポート日時
    backupSnoozeUntil: null                      // 警告スヌーズ期限
}
```

メンバーは RAW 定数から毎回再構築するので state には保存されない。
memberId 形式は `M_<名前>`（男性）/ `F_<名前>`（女性）。

---

## 色分け

| 対象 | 色 |
|---|---|
| 男性行 | 薄青 `#dbeafe`（# 列だけ `#bfdbfe`） |
| 女性行 | 薄ピンク `#fce7f3`（# 列だけ `#fbcfe8`） |
| ○ マーク | 赤 `#e11d48` |
| 土曜日ヘッダー | 青 `#2563eb` |
| 日曜日ヘッダー | 赤 `#dc2626` |

---

## 主要関数

| 関数 | 役割 |
|---|---|
| `buildMembers()` | RAW 定数からメンバー配列を生成 |
| `sortDates()` | `state.dates` を label(YYYY-MM-DD) の昇順で並び替え |
| `load()` / `save()` | localStorage 読み書き（load 時に sortDates） |
| `render()` | テーブル全体（thead / tbody / tfoot）を再描画 |
| `toggleCell(mid, did)` | 出席○のトグル |
| `addDate()` | 今日の日付で列を追加、sort 後にその列へ自動スクロール |
| `openDateModal(did)` / `saveDate()` / `deleteDate()` | 日付列の編集・削除（saveDate は sort 付き） |
| `exportJson()` / `importJson(file)` | JSON入出力（import 時に sort） |
| `resetAttendance()` | 出席データと日付列を全消去 |

### tfoot（合計行）の描画ロジック

`render()` 内で attendance を走査して各 `did` ごとの ○ 数をカウントし、`<tfoot>` を生成。
`<td>` に `position: sticky; bottom: 0` を付けて画面下部に固定。
sticky-left と sticky-bottom が交差する左下セルは z-index を 16 にして最前面に。

---

## 使用ライブラリ

- **Noto Sans JP**（Google Fonts） — フォント

外部依存はこれのみ。オフライン時はフォントが効かないだけで機能は動く。

---

## PWA（ホーム画面追加対応）

スマホブラウザの localStorage 自動削除（iOS の7日ITP等）対策として PWA 化。

### ユーザー操作（メンバー側）
- **Android Chrome**: メニュー → 「アプリをインストール」または「ホーム画面に追加」
- **iPhone Safari**: 共有ボタン → 「ホーム画面に追加」

追加後はホーム画面アイコンから起動。アドレスバー無しの全画面アプリ風に動く。

### Service Worker の戦略
- `service-worker.js` は Network First（オンラインなら最新、オフラインならキャッシュ）
- バージョン更新時は `CACHE_VERSION` を上げる → activate で旧キャッシュを削除
- 同一オリジンのみキャッシュ対象（Google Fonts はキャッシュしない）

### アイコン
- `make_icons.py` を実行すると `icon-192.png` / `icon-512.png` を再生成
- デザイン変更時は make_icons.py の `BG_COLOR` / `TEXT` を編集

---

## バックアップ警告（C案）

### 動作
- `state.lastBackupAt`（JSONエクスポート日時）と現在日時を比較
- `BACKUP_WARN_DAYS`（=7日）以上経過していて、かつデータがあれば起動時にモーダル表示
- 「今すぐJSON保存」→ `exportJson()` 実行、lastBackupAt 更新
- 「あとで」→ `BACKUP_SNOOZE_DAYS`（=3日）スヌーズ
- 一度もバックアップしていない状態でデータがあれば、初回も警告対象

### 注意
- データ未投入の初回ユーザーには警告しない
- 警告日数の調整は `BACKUP_WARN_DAYS` / `BACKUP_SNOOZE_DAYS` 定数で

---

## 修正時の注意

- `render()` 呼び出しで画面全体が再描画される設計。DOM直接操作は不要
- セル＆日付ヘッダーのクリックはテーブルへのイベント委任で処理
- ビューポートは `user-scalable=no` でピンチズーム禁止
- `max-height: calc(100dvh - 57px)` で iOS Safari のアドレスバー伸縮にも追従
