import { defineConfig } from 'vitepress'

export default defineConfig({
  lang: 'ja',
  title: 'Little Brother 日本語訳',
  description:
    'Cory Doctorow 著 Little Brother の日本語訳。CC BY-NC-SA 3.0 ライセンスの英語版をもとにした翻訳プロジェクトです。',

  base: '/little-brother-ja/',

  head: [
    ['meta', { name: 'robots', content: 'noindex' }],
    ['meta', { name: 'author', content: 'Cory Doctorow (原著); 翻訳: 高須正和 / TAKASU Masakazu' }],
  ],

  themeConfig: {
    siteTitle: 'Little Brother 日本語訳',

    nav: [
      { text: 'ホーム', link: '/' },
      { text: 'クレジット', link: '/credits' },
      { text: 'ライセンス', link: '/license' },
      {
        text: '翻訳方針',
        link: 'https://github.com/Nico-Tech-Shenzhen/little-brother-ja/blob/main/TRANSLATION_GUIDE.md',
      },
    ],

    sidebar: [
      {
        text: '前書き',
        items: [
          { text: '著者まえがき', link: '/ja/introduction' },
        ],
      },
      {
        text: '本文',
        items: [
          { text: '第1章', link: '/ja/ch01' },
          { text: '第2章', link: '/ja/ch02' },
          { text: '第3章', link: '/ja/ch03' },
          { text: '第4章', link: '/ja/ch04' },
          { text: '第5章', link: '/ja/ch05' },
          { text: '第6章', link: '/ja/ch06' },
          { text: '第7章', link: '/ja/ch07' },
          { text: '第8章', link: '/ja/ch08' },
          { text: '第9章', link: '/ja/ch09' },
          { text: '第10章', link: '/ja/ch10' },
          { text: '第11章', link: '/ja/ch11' },
          { text: '第12章', link: '/ja/ch12' },
          { text: '第13章', link: '/ja/ch13' },
          { text: '第14章', link: '/ja/ch14' },
          { text: '第15章', link: '/ja/ch15' },
          { text: '第16章', link: '/ja/ch16' },
          { text: '第17章', link: '/ja/ch17' },
          { text: '第18章', link: '/ja/ch18' },
          { text: '第19章', link: '/ja/ch19' },
          { text: '第20章', link: '/ja/ch20' },
          { text: '第21章', link: '/ja/ch21' },
        ],
      },
      {
        text: '後書き',
        items: [
          { text: 'エピローグ', link: '/ja/epilogue' },
          { text: 'あとがき（ブルース・シュナイアー）', link: '/ja/afterword-schneier' },
          { text: 'あとがき（bunnie Huang）', link: '/ja/afterword-huang' },
          { text: '参考文献', link: '/ja/bibliography' },
          { text: '謝辞', link: '/ja/acknowledgments' },
        ],
      },
      {
        text: '情報',
        items: [
          {
            text: '翻訳方針',
            link: 'https://github.com/Nico-Tech-Shenzhen/little-brother-ja/blob/main/TRANSLATION_GUIDE.md',
          },
          { text: 'コンテンツライセンス', link: '/license' },
          { text: 'クレジット', link: '/credits' },
        ],
      },
    ],

    footer: {
      message:
        '高須正和（@tks）による日本語訳です。原著は Cory Doctorow に帰属します。',
      copyright:
        '翻訳テキスト © 翻訳者 | 原著 © 2008 Cory Doctorow | CC BY-NC-SA 3.0',
    },

    editLink: {
      pattern: 'https://github.com/Nico-Tech-Shenzhen/little-brother-ja/edit/main/docs/:path',
      text: 'このページを編集',
    },
  },

  markdown: {
    lineNumbers: false,
  },
})
