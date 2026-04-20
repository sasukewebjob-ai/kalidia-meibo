# KALIDIA名簿 - CLAUDE.md

## プロジェクト概要

バドミントンサークル「KALIDIA」の**出欠名簿票**をWebアプリ化したもの。
スマホのChromeで動作し、タップで出席○を付けられる。データは `localStorage` に自動保存。
単一HTMLファイル（index.html）で完結するバニラJS製。ビルド不要、ブラウザで開くだけで動く。

姉妹アプリ「KALIDIAコート割」と同じ構成・同じメンバーリストを共有する。

---

## ファイル構成

```
KALIDIA名簿/
├── index.html          # アプリ本体（HTML/CSS/JS全込み）
├── members.txt         # メンバーリスト（編集はここだけ）
├── update_members.py   # members.txt → index.html を同期するスクリプト
├── CLAUDE.md           # このファイル
└── README.md           # GitHub公開用の説明
```

---

## メンバーの更新手順

1. `members.txt` を編集（追加・削除・名前変更）
2. 以下を実行：
   ```
   python update_members.py
   ```
3. `index.html` をブラウザで開き直す

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
| 日付列の追加 | 「＋日付」ボタンで末尾に今日の日付で列を追加 |
| 日付編集 | 日付ヘッダーをタップ→モーダルで日付変更・列削除 |
| 出席入力 | セルをタップで ○ ⇔ 空 のトグル |
| 自動保存 | `localStorage`（キー: `kalidia_roster_v1`）に即時保存 |
| JSONエクスポート | 全データを .json ファイルでダウンロード |
| JSONインポート | .json ファイルを読み込んで復元 |
| 全リセット | 日付列と出席データを全削除（メンバーは残る） |
| スマホ最適化 | 氏名列 sticky-left、日付ヘッダー sticky-top、44px セル |

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
    }
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
| `load()` / `save()` | localStorage 読み書き |
| `render()` | テーブル全体を再描画 |
| `toggleCell(mid, did)` | 出席○のトグル |
| `addDate()` | 今日の日付で列を追加 |
| `openDateModal(did)` / `saveDate()` / `deleteDate()` | 日付列の編集・削除 |
| `exportJson()` / `importJson(file)` | JSON入出力 |
| `resetAttendance()` | 出席データ全消去 |

---

## 使用ライブラリ

- **Noto Sans JP**（Google Fonts） — フォント

外部依存はこれのみ。オフライン時はフォントが効かないだけで機能は動く。

---

## 修正時の注意

- `render()` 呼び出しで画面全体が再描画される設計。DOM直接操作は不要
- セル＆日付ヘッダーのクリックはテーブルへのイベント委任で処理
- ビューポートは `user-scalable=no` でピンチズーム禁止
- `max-height: calc(100dvh - 57px)` で iOS Safari のアドレスバー伸縮にも追従
