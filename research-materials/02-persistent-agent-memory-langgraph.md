<!DOCTYPE html><!-- Last Published: Tue Jul 14 2026 21:47:57 GMT+0000 (Coordinated Universal Time) --><html data-wf-domain="focused.io" data-wf-page="69171d91c941b87f367ee7fb" data-wf-site="6915b44a5861a2536d561406" lang="en" data-wf-collection="69171d91c941b87f367ee7ca" data-wf-item-slug="persistent-agent-memory-in-langgraph"><head><meta charset="utf-8"/><link href="https://cdn.prod.website-files.com" rel="preconnect" crossorigin="anonymous"/><title>Persistent Agent Memory in LangGraph: Cross-Thread State and Memory Stores | Focused</title><meta content="Build persistent agent memory in LangGraph using checkpointers and memory stores. Learn how to manage cross-thread state and long-term memory for production agents." name="description"/><meta content="Persistent Agent Memory in LangGraph: Cross-Thread State and Memory Stores | Focused" property="og:title"/><meta content="Build persistent agent memory in LangGraph using checkpointers and memory stores. Learn how to manage cross-thread state and long-term memory for production agents." property="og:description"/><meta content="https://cdn.prod.website-files.com/69171c5b6a36fedc1f0d6866/69b18c5fc64f4cf183875baa_MemoryTiersOG.gif" property="og:image"/><meta content="Persistent Agent Memory in LangGraph: Cross-Thread State and Memory Stores | Focused" name="twitter:title"/><meta content="Build persistent agent memory in LangGraph using checkpointers and memory stores. Learn how to manage cross-thread state and long-term memory for production agents." name="twitter:description"/><meta content="https://cdn.prod.website-files.com/69171c5b6a36fedc1f0d6866/69b18c5fc64f4cf183875baa_MemoryTiersOG.gif" name="twitter:image"/><meta property="og:type" content="website"/><meta content="summary_large_image" name="twitter:card"/><meta content="width=device-width, initial-scale=1" name="viewport"/><link href="https://cdn.prod.website-files.com/6915b44a5861a2536d561406/css/focusedio.webflow.shared.720e5139e.min.css" rel="stylesheet" type="text/css" integrity="sha384-cg5ROe9uL/hvzkX7r5MX+q/x3SWKzc8441acHSbkRRaKw8ylWcjmTUO2o0fjKu+z" crossorigin="anonymous"/><script type="text/javascript">!function(o,c){var n=c.documentElement,t=" w-mod-";n.className+=t+"js",("ontouchstart"in o||o.DocumentTouch&&c instanceof DocumentTouch)&&(n.className+=t+"touch")}(window,document);</script><link href="https://cdn.prod.website-files.com/6915b44a5861a2536d561406/696d02b85269d6c69f2d5c34_favicon.png" rel="shortcut icon" type="image/x-icon"/><link href="https://cdn.prod.website-files.com/6915b44a5861a2536d561406/696d031cb646a7a2196561fc_webclip.png" rel="apple-touch-icon"/><link href="https://focused.io/lab/persistent-agent-memory-in-langgraph" rel="canonical"/><script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "@id": "https://focused.io/lab/persistent-agent-memory-in-langgraph#article",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://focused.io/lab/persistent-agent-memory-in-langgraph"
  },
  "headline": "Persistent Agent Memory in LangGraph",
  "description": "Build persistent agent memory in LangGraph using checkpointers and memory stores. Learn how to manage cross-thread state and long-term memory for production agents.",
  "url": "https://focused.io/lab/persistent-agent-memory-in-langgraph",
  "image": "https://cdn.prod.website-files.com/69171c5b6a36fedc1f0d6866/69b18c5fc64f4cf183875baa_MemoryTiersOG.gif",
  "datePublished": "2026-05-28T16:38:42.148Z",
  "dateModified": "2026-05-28T16:31:17.313Z",
  "author": {
    "@type": "Person",
    "name": "Austin Vance"
  },
  "publisher": {
    "@type": "Organization",
    "@id": "https://focused.io/#organization",
    "name": "Focused Labs Inc.",
    "url": "https://focused.io/",
    "logo": {
      "@type": "ImageObject",
      "url": "https://cdn.prod.website-files.com/6915b44a5861a2536d561406/6926f90025623396d545b2bc_footer-logo.svg"
    }
  },
  "articleSection": "Use Cases",
  "inLanguage": "en"
}
</script><link href="rss.xml" rel="alternate" title="RSS Feed" type="application/rss+xml"/><style>
body {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>

<style>
  .w-richtext table {
    width: 100%;
    border-collapse: collapse;
    margin: 1.5rem 0;
    font-size: 0.9375rem;
    line-height: 1.6;
    display: block;
    overflow-x: auto;
  }

  .w-richtext thead {
    position: sticky;
    top: 0;
  }

  .w-richtext thead th {
    background: #211659;
    color: #fff;
    font-weight: 700;
    text-align: left;
    padding: 0.75rem 1rem;
    font-size: 0.8125rem;
    letter-spacing: 0.025em;
    text-transform: uppercase;
    white-space: nowrap;
  }

  .w-richtext thead th:first-child {
    border-radius: 6px 0 0 0;
  }

  .w-richtext thead th:last-child {
    border-radius: 0 6px 0 0;
  }

  .w-richtext td,
  .w-richtext tbody th {
    padding: 0.625rem 1rem;
    border-bottom: 1px solid #eee;
    vertical-align: top;
  }

  .w-richtext td {
    color: #444;
  }

  .w-richtext tbody th {
    background: transparent;
    color: #222;
    font-weight: 600;
    text-align: left;
    text-transform: none;
    letter-spacing: normal;
    font-size: inherit;
    white-space: normal;
    border-radius: 0;
  }

  .w-richtext tr:last-child td,
  .w-richtext tr:last-child th {
    border-bottom: none;
  }

  .w-richtext tbody tr:nth-child(even) {
    background: #f9f7ff;
  }

  .w-richtext tbody tr:hover {
    background: #f0ecff;
  }

  .w-richtext td code,
  .w-richtext th code {
    font-family: 'Roboto Mono', monospace;
    font-size: 0.8125rem;
    background: #f5f8fa;
    padding: 0.125rem 0.375rem;
    border-radius: 3px;
  }

  .w-richtext td a {
    color: #8760f6;
    text-decoration: none;
  }

  .w-richtext td a:hover {
    text-decoration: underline;
  }

  @media (max-width: 767px) {
    .w-richtext table {
      font-size: 0.875rem;
    }
    .w-richtext th,
    .w-richtext td {
      padding: 0.5rem 0.75rem;
    }
  }
</style>

<script>
if (window.location.hostname.includes("webflow.io")) {
  const s = document.createElement("script");
  s.src = "https://www.bugherd.com/sidebarv2.js?apikey=bx0b67dz7z33s3s5a0ieaw";
  document.head.appendChild(s);
}
</script>

<link rel="preconnect" href="https://cdn.prod.website-files.com" crossorigin>
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@12/swiper-bundle.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/swiper@12/swiper-bundle.min.js"></script>

<script>
  window.WebFont = { load: function(){} };
</script>

<script async type="module"
src="https://cdn.jsdelivr.net/npm/@finsweet/attributes@2/attributes.js"
fs-scrolldisable
></script>

<script>
  WebFontConfig = {
    google: { families: [] }
  };
</script><!-- Finsweet Attributes -->
<script async type="module"
src="https://cdn.jsdelivr.net/npm/@finsweet/attributes@2/attributes.js"
fs-socialshare
></script><script src="https://cdn.prod.website-files.com/6915b44a5861a2536d561406%2F66ba5a08efe71070f98dd10a%2F696a8b0f1fb9a70c9f6c5d58%2Fkt39svjd-1.1.1.js" type="text/javascript"></script></head><body><div class="global-styles"><div class="style-overrides w-embed"><style>

/* Ensure all elements inherit the color from its parent */
a,
.w-input,
.w-select,
.w-tab-link,
.w-nav-link,
.w-nav-brand,
.w-dropdown-btn,
.w-dropdown-toggle,
.w-slider-arrow-left,
.w-slider-arrow-right,
.w-dropdown-link {
  color: inherit;
  text-decoration: inherit;
  font-size: inherit;
}

/* Focus state style for keyboard navigation for the focusable elements */
*[tabindex]:focus-visible,
  input[type="file"]:focus-visible {
   outline: 0.125rem solid #4d65ff;
   outline-offset: 0.125rem;
}

/* Get rid of top margin on first element in any rich text element */
.w-richtext > :not(div):first-child, .w-richtext > div:first-child > :first-child {
  margin-top: 0 !important;
}

/* Get rid of bottom margin on last element in any rich text element */
.w-richtext>:last-child, .w-richtext ol li:last-child, .w-richtext ul li:last-child {
	margin-bottom: 0 !important;
}

/* Prevent all click and hover interaction with an element */
.pointer-events-off {
	pointer-events: none;
}

/* Enables all click and hover interaction with an element */
.pointer-events-on {
  pointer-events: auto;
}

/* Create a class of .div-square which maintains a 1:1 dimension of a div */
.div-square::after {
	content: "";
	display: block;
	padding-bottom: 100%;
}

/* Make sure containers never lose their center alignment */
.container-medium,.container-small, .container-large {
	margin-right: auto !important;
  margin-left: auto !important;
}


/* Apply "..." after 3 lines of text */
.text-style-3lines {
	display: -webkit-box;
	overflow: hidden;
	-webkit-line-clamp: 3;
	-webkit-box-orient: vertical;
}

/* Apply "..." after 2 lines of text */
.text-style-2lines {
	display: -webkit-box;
	overflow: hidden;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
}

/* Adds inline flex display */
.display-inlineflex {
  display: inline-flex;
}

/* These classes are never overwritten */
.hide {
  display: none !important;
}

/* Remove default Webflow chevron from form select */
select{
  -webkit-appearance:none;
}


@media screen and (max-width: 991px) {
    .hide, .hide-tablet {
        display: none !important;
    }
}
  @media screen and (max-width: 767px) {
    .hide-mobile-landscape{
      display: none !important;
    }
}
  @media screen and (max-width: 479px) {
    .hide-mobile{
      display: none !important;
    }
}
 
.margin-0 {
  margin: 0rem !important;
}
  
.padding-0 {
  padding: 0rem !important;
}

.spacing-clean {
padding: 0rem !important;
margin: 0rem !important;
}

.margin-top {
  margin-right: 0rem !important;
  margin-bottom: 0rem !important;
  margin-left: 0rem !important;
}

.padding-top {
  padding-right: 0rem !important;
  padding-bottom: 0rem !important;
  padding-left: 0rem !important;
}
  
.margin-right {
  margin-top: 0rem !important;
  margin-bottom: 0rem !important;
  margin-left: 0rem !important;
}

.padding-right {
  padding-top: 0rem !important;
  padding-bottom: 0rem !important;
  padding-left: 0rem !important;
}

.margin-bottom {
  margin-top: 0rem !important;
  margin-right: 0rem !important;
  margin-left: 0rem !important;
}

.padding-bottom {
  padding-top: 0rem !important;
  padding-right: 0rem !important;
  padding-left: 0rem !important;
}

.margin-left {
  margin-top: 0rem !important;
  margin-right: 0rem !important;
  margin-bottom: 0rem !important;
}
  
.padding-left {
  padding-top: 0rem !important;
  padding-right: 0rem !important;
  padding-bottom: 0rem !important;
}
  
.margin-horizontal {
  margin-top: 0rem !important;
  margin-bottom: 0rem !important;
}

.padding-horizontal {
  padding-top: 0rem !important;
  padding-bottom: 0rem !important;
}

.margin-vertical {
  margin-right: 0rem !important;
  margin-left: 0rem !important;
}
  
.padding-vertical {
  padding-right: 0rem !important;
  padding-left: 0rem !important;
}

/* Apply "..." at 100% width */
.truncate-width { 
		width: 100%; 
    white-space: nowrap; 
    overflow: hidden; 
    text-overflow: ellipsis; 
}
/* Removes native scrollbar */
.no-scrollbar {
    -ms-overflow-style: none;
    overflow: -moz-scrollbars-none; 
}

.no-scrollbar::-webkit-scrollbar {
    display: none;
}
.numbers-item {
	border-color: var(--_brand-colors---purple);
}

.numbers-item:last-of-type {
	border-color: transparent;
}


.heading-rich-text strong {
	background: linear-gradient(to right,#7953cd 20%,#00affa 30%,#0190cd 70%,#764ada 80%);
	animation: textShine 10s ease-in-out infinite;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  text-fill-color: transparent;    
	background-size: 500%;
  -webkit-background-clip: text;
  background-clip: text;
}

@keyframes textShine {
  0% {
    background-position: 0%
  }

  to {
    background-position: 100%
  }
}
.feature_card-swiper {
  width: 100% !important;
  max-width: 100% !important;
}

.feature_card-swiper-wrapper {
  width: 100% !important;
  max-width: 100% !important;
}

.feature_card-swiper-slide {
  width: 100% !important;
  max-width: 100% !important;
  flex-shrink: 0 !important;
}

[data-wf--section--background="purple-orange-gradient"] {
  background-image: radial-gradient(50% 50% at 45% 35%, rgb(252, 195, 158), rgba(7, 58, 255, 0)), 
radial-gradient(80% 91% at 0px -2%, rgb(146, 75, 173), rgba(255, 0, 0, 0) 99%), 
radial-gradient(100% 91% at 83% 7%, rgb(249, 167, 114) 2%, rgba(255, 0, 0, 0) 99%), 
radial-gradient(142% 91% at -6% 74%, rgb(255, 255, 255) 1%, rgba(255, 0, 0, 0) 99%), 
radial-gradient(142% 91% at 111% 84%, rgb(255, 255, 255), rgb(255, 255, 255));
}

.lottie-animation-wrapper {
  position: var(--pos, relative);
  width: var(--w, auto);
  height: var(--h, auto);
  top: var(--top, auto);
  bottom: var(--bottom, auto);
  left: var(--left, auto);
  right: var(--right, auto);
}

.lottie-box {
  width: 100%;
  height: 100%;
}

.section {
  position: relative;
  background-color: transparent;
  color: var(--color-scheme-1--headings-color);
}

.section:where(.w-variant-9d0feaa9-b85a-1a01-ab3a-3ae2f2599d04) {
  position: relative;
  background-color: var(--_brand-colors---blue-light);
}

.section:where(.w-variant-a8f5da4f-54ae-37b9-b220-5fae805c76a4) {
  background-image: linear-gradient(white, rgba(255, 255, 255, 0)), linear-gradient(101deg, rgb(252, 243, 236) 11%, rgb(239, 234, 253) 94%);
}

.section:where(.w-variant-f7cee39c-a0b1-0b15-c488-74bd4d4e8e83) {
  background-image: linear-gradient(170deg, rgb(245, 248, 250) 55%, rgba(233, 156, 55, 0.8));
}

.section:where(.w-variant-3760380e-980b-23f3-54f3-d8243b37cf92) {
  background-image: linear-gradient(180deg, transparent, var(--_brand-colors---blue-light));
}

.page-button::before {
	content: "0";
}

.page-button.w--current {
  color: var(--_brand-colors---dark-purple);
  text-decoration: underline;
}

.text-rich-text blockquote {
	margin-top: 2.5rem;
  margin-bottom: 2.5rem;
  padding: 2.5rem;
  border-radius: 1.25rem;
  background-image: linear-gradient(100deg, rgb(252, 243, 236) 10%, rgb(239, 234, 253) 90%);
  color: var(--color-scheme-1--headings-color);
  font-size: 2rem;
  line-height: 2.625rem;
  font-weight: 700;
}

.is-scrolled .navbar14_container {
	max-height: 3.875rem
}

.is-scrolled .info-bar[data-wf--infobar--variant="bottom"] {
	transform: translateY(0%);
}

 
.is-scrolled .navbar14_link,
.is-scrolled .navbar14_dropdown-toggle {
	 padding: .5rem .75rem 0.75rem;
   margin-top: 0.75rem;
}

select.hs-input {
	color: rgba(0,0,0,0.5);
	font-size: 1rem;
}

.lottie-animation-wrapper svg {
    position: relative;
}
.lottie-animation-wrapper svg image {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    width: 140% !important;
    height: 140% !important;
    object-fit: cover !important;
    display: none;
}

.hs-form-field > label {
	display: none;
}


#case-gate .hs-form-field > label {
	display: block;
}

.hs-form-booleancheckbox {
	margin-bottom: 0 !important;
}

@media screen and (max-width: 640px) {
 	.heading-style.smaller-on-mobile {
		font-size: 1.2rem
	}
}

@media screen and (max-width: 991px) {
    [data-wf--header---two-columns--variant="reversed-light-purple-bg-shadow-2"] .lottie-animation-wrapper {
      display: none;
    }       
}


@media screen and (max-width: 991px) {
    .spacer:where(.w-variant-301f2f49-ba85-8507-11a1-c51f9e40b381) {
        height: 0 !important;
    }
    
    .slot {
			width: 100%;
		}
}

.text-rich-text pre {
	display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em
}


/* Code NIE w pre (inline, np. w tekście) */
code {
  background: #f0f0f0;
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-size: 0.9em;
}
/* Code W pre – nadpisujesz, żeby bloki wyglądały inaczej */
pre code {
  background: none;
  padding: 0;
  border-radius: 0;
  font-size: inherit;
}

.navbar14_dropdown-toggle.w--open {
	height: auto;
}

</style>

<style>
.page-button[href$="_page=10"]::before,
.page-button[href$="_page=11"]::before,
.page-button[href$="_page=12"]::before,
.page-button[href$="_page=13"]::before,
.page-button[href$="_page=14"]::before,
.page-button[href$="_page=15"]::before,
.page-button[href$="_page=16"]::before,
.page-button[href$="_page=17"]::before,
.page-button[href$="_page=18"]::before,
.page-button[href$="_page=19"]::before,
.page-button[href$="_page=20"]::before,
.page-button[href$="_page=21"]::before,
.page-button[href$="_page=22"]::before,
.page-button[href$="_page=23"]::before,
.page-button[href$="_page=24"]::before,
.page-button[href$="_page=25"]::before,
.page-button[href$="_page=26"]::before,
.page-button[href$="_page=27"]::before,
.page-button[href$="_page=28"]::before,
.page-button[href$="_page=29"]::before,
.page-button[href$="_page=30"]::before {
  content: "";
}
</style></div><div class="color-schemes w-embed"><style>
/* Color Schemes Controls*/
<meta name="relume-color-schemes" content="false"/>

  .color-scheme-1 {
/*All sections should point to Color Scheme 1*/

  }

  .color-scheme-2 {
    --color-scheme-1--text: var(--color-scheme-2--text);
    --color-scheme-1--background: var(--color-scheme-2--background);
    --color-scheme-1--foreground: var(--color-scheme-2--foreground);
    --color-scheme-1--border: var(--color-scheme-2--border);
    --color-scheme-1--accent: var(--color-scheme-2--accent);
  }

  .color-scheme-3 {
    --color-scheme-1--text: var(--color-scheme-3--text);
    --color-scheme-1--background: var(--color-scheme-3--background);
    --color-scheme-1--foreground: var(--color-scheme-3--foreground);
    --color-scheme-1--border: var(--color-scheme-3--border);
    --color-scheme-1--accent: var(--color-scheme-3--accent);
  }

  .color-scheme-4 {
    --color-scheme-1--text: var(--color-scheme-4--text);
    --color-scheme-1--background: var(--color-scheme-4--background);
    --color-scheme-1--foreground: var(--color-scheme-4--foreground);
    --color-scheme-1--border: var(--color-scheme-4--border);
    --color-scheme-1--accent: var(--color-scheme-4--accent);
  }

  .color-scheme-5 {
    --color-scheme-1--text: var(--color-scheme-5--text);
    --color-scheme-1--background: var(--color-scheme-5--background);
    --color-scheme-1--foreground: var(--color-scheme-5--foreground);
    --color-scheme-1--border: var(--color-scheme-5--border);
    --color-scheme-1--accent: var(--color-scheme-5--accent);
  }

  .color-scheme-6 {
    --color-scheme-1--text: var(--color-scheme-6--text);
    --color-scheme-1--background: var(--color-scheme-6--background);
    --color-scheme-1--foreground: var(--color-scheme-6--foreground);
    --color-scheme-1--border: var(--color-scheme-6--border);
    --color-scheme-1--accent: var(--color-scheme-6--accent);
  }

  .color-scheme-7 {
    --color-scheme-1--text: var(--color-scheme-7--text);
    --color-scheme-1--background: var(--color-scheme-7--background);
    --color-scheme-1--foreground: var(--color-scheme-7--foreground);
    --color-scheme-1--border: var(--color-scheme-7--border);
    --color-scheme-1--accent: var(--color-scheme-7--accent);
  }

  .color-scheme-8 {
    --color-scheme-1--text: var(--color-scheme-8--text);
    --color-scheme-1--background: var(--color-scheme-8--background);
    --color-scheme-1--foreground: var(--color-scheme-8--foreground);
    --color-scheme-1--border: var(--color-scheme-8--border);
    --color-scheme-1--accent: var(--color-scheme-8--accent);
  }

  .color-scheme-9 {
    --color-scheme-1--text: var(--color-scheme-9--text);
    --color-scheme-1--background: var(--color-scheme-9--background);
    --color-scheme-1--foreground: var(--color-scheme-9--foreground);
    --color-scheme-1--border: var(--color-scheme-9--border);
    --color-scheme-1--accent: var(--color-scheme-9--accent);
  }

  .color-scheme-10 {
    --color-scheme-1--text: var(--color-scheme-10--text);
    --color-scheme-1--background: var(--color-scheme-10--background);
    --color-scheme-1--foreground: var(--color-scheme-10--foreground);
    --color-scheme-1--border: var(--color-scheme-10--border);
    --color-scheme-1--accent: var(--color-scheme-10--accent);
  }
  
/* Inherit slider dot colors */
.w-slider-dot {
  background-color: var(--color-scheme-1--text);
  opacity: 0.20;
}

.w-slider-dot.w-active {
  background-color: var(--color-scheme-1--text);
  opacity: 1;
}

/* Override .w-slider-nav-invert styles */
.w-slider-nav-invert .w-slider-dot {
  background-color: var(--color-scheme-1--text) !important;
  opacity: 0.20 !important;
}

.w-slider-nav-invert .w-slider-dot.w-active {
  background-color: var(--color-scheme-1--text) !important;
  opacity: 1 !important;
}

</style></div><div class="global-styles w-embed"><style>

/* All paragraph elements inside Hubspot form */
.hs-form>p {
 margin-top:1rem;
 margin-bottom:1rem;
 }
 
 /* Set margin right 0 for input wrapper */
 .hs-form .input {
 margin-right: 0 !important;
 }

/* Max width of fieldset element inside form */
.hs-form>fieldset {
 max-width: 100% !important;
 }

/* Form Input */
.hs-input {
 width: 100% !important;
 }

/* Radio Inputs */
.hs-input[type=radio] {
 width: auto !important;
 margin-right: 0.5rem;
 min-height: auto !important;
}

/* Checkbox Labels */
.hs-form-checkbox>label {
font-weight: 400 !important;
}

/* Error messages label margin */
.hs-error-msgs>label {
 margin-bottom: 0px !important;
 }


/*Custom Checkbox*/
.hs-input[type=checkbox] {
  width: 1rem !important;
  height: 1rem !important;
  margin-right: 0.5rem !important;
  min-height: auto !important;
}

.hs-input[type=checkbox]:focus {
  box-shadow: 0 0 3px 1px #bdfd2e;
}

.hs-input[type=checkbox]:checked {
 accent-color: #111;
 outline: 2px solid #111;
}

.hs-form-booleancheckbox-display>span {
 margin-left: 0 !important;
 }
 
@media screen and (max-width: 991px) {
	fieldset.form-columns-2 .hs-form-field {
  	width: 100% !important;
	}
}

</style></div></div><div class="page-wrapper navbar-on-page"><div class="main-wrapper max-width-full"><div data-wf--infobar--variant="base" class="info-bar"><div class="info-bar_component-wrapper"><div class="padding-global reset-padding"><div class="container-large"><div class="info-bar_component"><div class="info-bar-left-col"><div class="info-bar-heading">Most AI projects fail. Yours doesn’t have to.</div><div class="info-bar-paragraph">Reserve your spot today and get a production-ready Agent Blueprint in just 3 weeks</div></div><div class="info-bar-right-col"><div class="info-bar-right-col-spots-wrapper"><div class="info-bar-heading is-number">6</div><div class="info-bar-paragraph is-counter"><strong>spots</strong>‍<br/>‍<strong>available</strong></div></div><div class="info-bar-right-col-button-wrapper"><a data-wf--button--variant="inverted" href="/agent-blueprint" class="button w-variant-6ad34387-476b-429a-1577-69de26fd7dbd navbutton w-inline-block"><div><strong>Register for Your Agent Blueprint</strong></div></a></div></div></div></div></div></div></div><div data-animation="default" class="navbar14_component w-nav" data-easing2="ease" fs-scrolldisable-element="smart-nav" data-easing="ease" data-collapse="medium" data-w-id="4d2ad485-bc76-b179-58db-3b0d49806479" role="banner" data-duration="400" data-wf--navigation--variant="base"><div class="navbar14_container"><a href="/" class="navbar14_logo-link w-nav-brand"><div class="navbar14_logo w-embed"><svg xmlns="http://www.w3.org/2000/svg" class="max-w-full lg:w-auto xl:max-w-none" width="100%" height="100%" viewBox="0 0 157 38" fill="none" preserveAspectRatio="xMidYMid meet" aria-hidden="true" role="img">
  <path d="M45.8096 9.85132H57.5138V13.1369H49.2611V17.3186H57.3589V20.6042H49.2611V28.1267H45.8096V9.85132Z" fill="#211659"/>
  <path d="M61.3965 16.9536C61.3965 14.5862 61.9939 12.7498 63.1886 11.4444C64.3834 10.139 66.0317 9.48633 68.1336 9.48633C70.2355 9.48633 71.8838 10.139 73.0786 11.4444C74.2734 12.7498 74.8707 14.5862 74.8707 16.9536V21.0246C74.8707 23.4584 74.2734 25.3169 73.0786 26.5891C71.8838 27.8613 70.2355 28.4919 68.1336 28.4919C66.0317 28.4919 64.3723 27.8613 63.1886 26.5891C61.9939 25.3169 61.3965 23.4584 61.3965 21.0246V16.9536ZM68.1336 25.3722C68.7642 25.3722 69.2841 25.2727 69.7045 25.0735C70.1249 24.8744 70.4678 24.5868 70.7223 24.2217C70.9767 23.8567 71.1648 23.4252 71.2754 22.9163C71.375 22.4075 71.4303 21.8543 71.4303 21.2459V16.7545C71.4303 16.1792 71.375 15.6371 71.2422 15.1393C71.1205 14.6304 70.9325 14.199 70.6669 13.8339C70.4014 13.4689 70.0696 13.1812 69.6492 12.96C69.2288 12.7387 68.731 12.6392 68.1336 12.6392C67.5362 12.6392 67.0384 12.7498 66.618 12.96C66.1977 13.1812 65.8658 13.4689 65.6003 13.8339C65.3348 14.199 65.1467 14.6304 65.025 15.1393C64.9033 15.6482 64.837 16.1903 64.837 16.7545V21.2459C64.837 21.8543 64.8923 22.4075 64.9918 22.9163C65.0914 23.4252 65.2795 23.8567 65.545 24.2217C65.7994 24.5868 66.1423 24.8744 66.5627 25.0735C66.9831 25.2727 67.503 25.3722 68.1336 25.3722Z" fill="#211659"/>
  <path d="M85.1258 25.3718C85.7895 25.3718 86.3316 25.2723 86.763 25.0731C87.1834 24.874 87.5153 24.6085 87.7587 24.2656C87.991 23.9226 88.1569 23.5354 88.2454 23.0929C88.3339 22.6504 88.3782 22.1969 88.3782 21.7212V21.2565H91.8297V21.7212C91.8297 23.9005 91.2655 25.571 90.1261 26.7436C88.9866 27.9162 87.3272 28.5026 85.1479 28.5026C82.9686 28.5026 81.3977 27.872 80.1808 26.5998C78.9639 25.3276 78.3555 23.4691 78.3555 21.0353V16.9643C78.3555 15.8027 78.5103 14.7517 78.8201 13.8225C79.1298 12.8932 79.5834 12.1078 80.1808 11.4772C80.7671 10.8466 81.4862 10.3488 82.3269 10.0169C83.1677 9.674 84.097 9.50806 85.1479 9.50806C86.1989 9.50806 87.1834 9.66293 88.0242 9.97269C88.8649 10.2824 89.5619 10.736 90.1261 11.3334C90.6903 11.9308 91.1217 12.6388 91.4093 13.4795C91.697 14.3203 91.8408 15.2495 91.8408 16.3005V16.7651H88.3893V16.3005C88.3893 15.8691 88.3339 15.4265 88.2344 14.9951C88.1348 14.5637 87.9578 14.1654 87.7144 13.8225C87.4711 13.4795 87.1392 13.1919 86.7188 12.9707C86.2984 12.7494 85.7785 12.6498 85.1479 12.6498C84.5727 12.6498 84.0748 12.7605 83.6545 12.9707C83.2341 13.1919 82.8911 13.4795 82.6146 13.8557C82.338 14.2318 82.1278 14.6632 81.9951 15.161C81.8623 15.6589 81.7959 16.1788 81.7959 16.7209V21.3119C81.7959 21.9092 81.8513 22.4513 81.984 22.9491C82.1057 23.4469 82.2938 23.8784 82.5593 24.2434C82.8248 24.6085 83.1677 24.8961 83.5881 25.0953C84.0085 25.2944 84.5284 25.394 85.1368 25.394L85.1258 25.3718Z" fill="#211659"/>
  <path d="M108.69 9.85132V21.81C108.69 23.9008 108.137 25.5381 107.031 26.7218C105.924 27.9055 104.287 28.5029 102.108 28.5029C99.9283 28.5029 98.291 27.9055 97.1848 26.7218C96.0785 25.5381 95.5254 23.9008 95.5254 21.81V9.85132H98.9769V21.81C98.9769 22.8941 99.2314 23.7349 99.7292 24.3433C100.238 24.9518 101.024 25.2615 102.108 25.2615C103.192 25.2615 103.977 24.9628 104.486 24.3433C104.995 23.7349 105.249 22.8941 105.249 21.81V9.85132H108.701H108.69Z" fill="#211659"/>
  <path d="M122.076 15.4491C122.076 14.7189 121.788 14.0773 121.224 13.5463C120.66 13.0042 119.864 12.7387 118.835 12.7387C117.961 12.7387 117.275 12.9157 116.766 13.2697C116.257 13.6237 116.014 14.1105 116.014 14.7189C116.014 15.0287 116.069 15.3163 116.202 15.5708C116.323 15.8252 116.534 16.0465 116.843 16.2456C117.142 16.4447 117.551 16.6217 118.049 16.7766C118.547 16.9315 119.178 17.0863 119.941 17.2191C121.855 17.5731 123.315 18.1483 124.333 18.967C125.34 19.7856 125.848 20.9914 125.848 22.5955V22.9053C125.848 23.7571 125.694 24.5315 125.395 25.2174C125.096 25.9032 124.654 26.4896 124.078 26.9763C123.503 27.4631 122.806 27.8392 121.988 28.0936C121.169 28.3591 120.24 28.4919 119.222 28.4919C118.016 28.4919 116.965 28.3259 116.047 27.983C115.129 27.6401 114.365 27.1754 113.757 26.5781C113.149 25.9807 112.684 25.2727 112.374 24.4651C112.064 23.6575 111.898 22.7725 111.898 21.8101V21.0246H115.35V21.6552C115.35 22.7504 115.671 23.6243 116.301 24.277C116.932 24.9297 117.928 25.2616 119.266 25.2616C120.306 25.2616 121.08 25.0404 121.589 24.5868C122.098 24.1332 122.353 23.5912 122.353 22.9716C122.353 22.673 122.297 22.3964 122.198 22.1198C122.098 21.8433 121.91 21.6109 121.645 21.3897C121.379 21.1684 121.025 20.9804 120.572 20.8034C120.118 20.6264 119.543 20.4826 118.846 20.3609C117.928 20.206 117.076 19.9958 116.312 19.7414C115.549 19.4869 114.885 19.155 114.31 18.7347C113.735 18.3143 113.303 17.7943 112.994 17.1638C112.684 16.5332 112.529 15.7699 112.529 14.8628V14.7079C112.529 13.9556 112.684 13.2697 112.983 12.6281C113.292 11.9975 113.713 11.4444 114.266 10.9687C114.819 10.493 115.483 10.128 116.246 9.87352C117.02 9.61908 117.883 9.48633 118.846 9.48633C119.93 9.48633 120.881 9.6412 121.722 9.9399C122.563 10.2496 123.26 10.659 123.824 11.1789C124.388 11.6988 124.82 12.2962 125.107 12.9821C125.395 13.6569 125.539 14.376 125.539 15.1172V16.0575H122.087V15.4269L122.076 15.4491Z" fill="#211659"/>
  <path d="M129.687 9.85132H141.225V13.1369H133.127V17.3186H140.904V20.6042H133.127V24.8301H141.535V28.1267H129.676V9.85132H129.687Z" fill="#211659"/>
  <path d="M145.396 9.85132H150.307C152.575 9.85132 154.257 10.3823 155.352 11.4333C156.447 12.4842 157 14.1215 157 16.334V21.6551C157 23.8676 156.447 25.5049 155.352 26.5559C154.257 27.6068 152.575 28.1378 150.307 28.1378H145.396V9.85132ZM150.307 24.8411C151.513 24.8411 152.354 24.5535 152.83 23.9893C153.305 23.4251 153.549 22.5401 153.549 21.3343V16.3229C153.549 15.272 153.305 14.4865 152.83 13.9445C152.354 13.4024 151.513 13.1369 150.307 13.1369H148.847V24.8411H150.307Z" fill="#211659"/>
  <path d="M18.2865 37.2866C28.3858 37.2866 36.573 29.0995 36.573 19.0001C36.573 8.90076 28.3858 0.713623 18.2865 0.713623C8.18714 0.713623 0 8.90076 0 19.0001C0 29.0995 8.18714 37.2866 18.2865 37.2866Z" fill="#211659"/>
  <path d="M24.4815 11.7206V7.69385C17.1249 7.69385 11.1621 13.6566 11.1621 21.0243H14.9455C12.6113 23.4249 11.1621 26.6994 11.1621 30.3058H15.1889V21.0243L24.4815 21.0132V16.9864C20.864 16.9864 17.5895 18.4356 15.1889 20.7809V11.7317H24.4815V11.7206Z" fill="white"/>
</svg></div></a><nav role="navigation" id="w-node-_4d2ad485-bc76-b179-58db-3b0d4980647d-49806479" class="navbar14_menu w-nav-menu"><div class="navbar14_menu-link-wrapper"><div class="navbar14_menu-links"><a href="/about" class="navbar14_link w-nav-link">About</a><div data-delay="200" data-hover="true" data-w-id="4d2ad485-bc76-b179-58db-3b0d49806482" class="navbar14_menu-dropdown w-dropdown"><div class="navbar14_dropdown-toggle w-dropdown-toggle"><a href="/capabilities" class="capabilities-link w-inline-block"></a><div>Capabilities</div><div class="dropdown-chevron w-embed"><svg width=" 100%" height=" 100%" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
<path fill-rule="evenodd" clip-rule="evenodd" d="M2.55806 6.29544C2.46043 6.19781 2.46043 6.03952 2.55806 5.94189L3.44195 5.058C3.53958 4.96037 3.69787 4.96037 3.7955 5.058L8.00001 9.26251L12.2045 5.058C12.3021 4.96037 12.4604 4.96037 12.5581 5.058L13.4419 5.94189C13.5396 6.03952 13.5396 6.19781 13.4419 6.29544L8.17678 11.5606C8.07915 11.6582 7.92086 11.6582 7.82323 11.5606L2.55806 6.29544Z" fill="currentColor"/>
</svg></div></div><nav class="navbar14_dropdown-list w-dropdown-list"><div class="navbar14_dropdown-list-wrapper"><a href="/capabilities/custom-agents" class="navbar14_dropdown-link w-dropdown-link">Custom Agents</a><a href="/capabilities/reliable-rag" class="navbar14_dropdown-link w-dropdown-link">Reliable RAG</a><a href="/capabilities/custom-software-development" class="navbar14_dropdown-link w-dropdown-link">Custom Software Development</a><a href="/capabilities/eval-driven-development" class="navbar14_dropdown-link w-dropdown-link">Eval Driven Development</a><a href="/capabilities/observability" class="navbar14_dropdown-link w-dropdown-link">Observability</a></div></nav></div><a href="/langchain" class="navbar14_link w-nav-link">LangChain</a><a href="/case-studies" class="navbar14_link w-nav-link">Case Studies</a><a href="/lab" class="navbar14_link w-nav-link">Focused Lab</a></div><div id="w-node-_4d2ad485-bc76-b179-58db-3b0d49806497-49806479" class="navbar14_button-wrapper"><a data-wf--button--variant="base" href="/contact" class="button navbutton w-inline-block"><div>Contact us</div><div class="icon-embed-xxsmall w-embed"><svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 16 16" fill="none" preserveAspectRatio="xMidYMid meet" aria-hidden="true" role="img">
<g clip-path="url(#clip0_38_3)">
<path d="M9.59961 1.70007L14.9996 8.00007L9.59961 14.3001" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
<path d="M0.898438 8.00006H14.9991" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
</g>
<defs>
<clipPath id="clip0_38_3">
<rect width="16" height="16" fill="white"/>
</clipPath>
</defs>
</svg></div></a></div></div></nav><div class="navbar14_menu-button w-nav-button"><div class="menu-icon2"><div class="menu-icon2_line-top"></div><div class="menu-icon2_line-middle"><div class="menu-icon1_line-middle-inner"></div></div><div class="menu-icon2_line-bottom"></div></div></div></div></div><header data-wf--section--background="base" class="section"><div class="anchor"></div><div class="padding-global"><div class="container-large"><div data-wf--spacer--variant="80px" class="spacer w-variant-d1bdc13f-1173-7a2d-b2b7-b03f39141b00"></div><div><div data-wf--content-wrapper--variant="base" class="content-wrapper"><div data-wf--spacer--variant="0px" class="spacer w-variant-301f2f49-ba85-8507-11a1-c51f9e40b381"></div><div class="content max-width-940 margin-horizontal-auto"><span data-wf--label--variant="fill-purple" class="heading-label w-variant-0884fcc4-e024-6b31-6d48-856d3ff36503">Use Cases</span></div><div data-wf--spacer--variant="0px" class="spacer w-variant-301f2f49-ba85-8507-11a1-c51f9e40b381"></div></div><div data-wf--content-wrapper--variant="base" class="content-wrapper"><div data-wf--spacer--variant="32px" class="spacer w-variant-29bd306d-eb12-24af-2435-e8c07bc89a72"></div><div class="content max-width-940 margin-horizontal-auto"><h1 data-wf--heading--variant="heading-style-h2" class="heading-style w-variant-eb7094f4-0e88-b38d-4a44-09af707e4a20">Persistent Agent Memory in LangGraph</h1><p data-wf--paragraph--variant="paragraph-20px" class="paragraph w-variant-5742efab-d3c1-da19-d677-debf9d157f14">Build stateful AI agents with LangGraph memory persistence. Implement checkpointers, long-term memory stores, and cross-session state.</p><p data-wf--paragraph--variant="paragraph-20px" class="paragraph w-variant-5742efab-d3c1-da19-d677-debf9d157f14 text-weight-bold">Mar 10, 2026</p></div><div data-wf--spacer--variant="32px" class="spacer w-variant-29bd306d-eb12-24af-2435-e8c07bc89a72"></div></div></div><div data-wf--spacer--variant="0px" class="spacer w-variant-301f2f49-ba85-8507-11a1-c51f9e40b381"></div></div></div></header><header data-wf--section--background="base" class="section"><div class="anchor"></div><div class="padding-global"><div class="container-large"><div data-wf--spacer--variant="0px" class="spacer w-variant-301f2f49-ba85-8507-11a1-c51f9e40b381"></div><div><div data-wf--content-wrapper--variant="base" class="content-wrapper"><div data-wf--spacer--variant="0px" class="spacer w-variant-301f2f49-ba85-8507-11a1-c51f9e40b381"></div><div class="content max-width-940 margin-horizontal-auto"><div class="_w-full"><div class="blog-author-with-share"><div class="blog-author-with-share-author"><div>By</div><div>Austin Vance</div></div><div class="blog-author-with-share-buttons"><div>Share:</div><div class="footer-grid--item footer--social"><a fs-socialshare-element="linkedin" href="#" class="social-icon-button w-inline-block"><div class="social-icon-button-icon w-embed"><svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 33 32" fill="none" preserveAspectRatio="xMidYMid meet" aria-hidden="true" role="img">
									<g clip-path="url(#clip0_8001_1572)">
										<path d="M11.8699 12.874H8.82202C8.68675 12.874 8.57715 12.9837 8.57715 13.1189V22.9104C8.57715 23.0456 8.68675 23.1552 8.82202 23.1552H11.8699C12.0052 23.1552 12.1148 23.0456 12.1148 22.9104V13.1189C12.1148 12.9837 12.0052 12.874 11.8699 12.874Z" fill="currentColor"/>
										<path d="M10.3471 8.00684C9.23815 8.00684 8.33594 8.90807 8.33594 10.0158C8.33594 11.1241 9.23815 12.0257 10.3471 12.0257C11.4553 12.0257 12.3567 11.124 12.3567 10.0158C12.3568 8.90807 11.4553 8.00684 10.3471 8.00684Z" fill="currentColor"/>
										<path d="M19.6217 12.6309C18.3975 12.6309 17.4926 13.1571 16.9438 13.755V13.1191C16.9438 12.9839 16.8342 12.8742 16.6989 12.8742H13.78C13.6448 12.8742 13.5352 12.9839 13.5352 13.1191V22.9106C13.5352 23.0458 13.6448 23.1554 13.78 23.1554H16.8212C16.9565 23.1554 17.0661 23.0458 17.0661 22.9106V18.0661C17.0661 16.4336 17.5095 15.7976 18.6475 15.7976C19.8869 15.7976 19.9854 16.8171 19.9854 18.15V22.9106C19.9854 23.0459 20.095 23.1555 20.2302 23.1555H23.2726C23.4078 23.1555 23.5174 23.0459 23.5174 22.9106V17.5398C23.5174 15.1124 23.0546 12.6309 19.6217 12.6309Z" fill="currentColor"/>
									</g>
									<defs>
										<clipPath id="clip0_8001_1572">
											<rect width="15.1822" height="15.1822" fill="currentColor" transform="translate(8.33594 7.99023)"/>
										</clipPath>
									</defs>
								</svg></div></a><a fs-socialshare-element="facebook" href="#" class="social-icon-button w-inline-block"><div class="social-icon-button-icon w-embed"><svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 32 32" fill="none" preserveAspectRatio="xMidYMid meet" aria-hidden="true" role="img">
									<path fill-rule="evenodd" clip-rule="evenodd" d="M17.1302 25.5701V16.8224H20.193L20.6515 13.4132H17.1302V11.2366C17.1302 10.2495 17.4161 9.5769 18.8925 9.5769L20.7755 9.57606V6.5269C20.4498 6.48543 19.3321 6.39258 18.0317 6.39258C15.3168 6.39258 13.4582 7.98131 13.4582 10.899V13.4132H10.3877V16.8224H13.4582V25.5701H17.1302Z" fill="currentColor"/>
								</svg></div></a><a fs-socialshare-element="x" href="#" class="social-icon-button w-inline-block"><div class="social-icon-button-icon w-embed"><svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 33 32" fill="none" preserveAspectRatio="xMidYMid meet" aria-hidden="true" role="img">
									<path d="M21.2678 8.79004H23.7183L18.3647 14.8827L24.6629 23.1732H19.7313L15.8689 18.1449L11.4493 23.1732H8.99718L14.7234 16.6565L8.68164 8.79004H13.7382L17.2296 13.386L21.2678 8.79004ZM20.4077 21.7127H21.7657L13.0004 10.1739H11.5434L20.4077 21.7127Z" fill="currentColor"/>
								</svg></div></a></div></div></div></div></div><div data-wf--spacer--variant="80px" class="spacer w-variant-d1bdc13f-1173-7a2d-b2b7-b03f39141b00"></div></div></div><div data-wf--spacer--variant="0px" class="spacer w-variant-301f2f49-ba85-8507-11a1-c51f9e40b381"></div></div></div></header><header data-wf--section--background="base" class="section"><div class="anchor"></div><div class="padding-global"><div class="container-large"><div data-wf--spacer--variant="0px" class="spacer w-variant-301f2f49-ba85-8507-11a1-c51f9e40b381"></div><div><div data-wf--content-wrapper--variant="base" class="content-wrapper"><div data-wf--spacer--variant="0px" class="spacer w-variant-301f2f49-ba85-8507-11a1-c51f9e40b381"></div><div class="content max-width-940 margin-horizontal-auto"><div data-wf--image--variant="base" class="header-two-column-col-img-wrapper"><img src="https://cdn.prod.website-files.com/69171c5b6a36fedc1f0d6866/69b18c5fc64f4cf183875baa_MemoryTiersOG.gif" loading="lazy" alt="" class="header-two-column-col-img"/></div></div><div data-wf--spacer--variant="80px" class="spacer w-variant-d1bdc13f-1173-7a2d-b2b7-b03f39141b00"></div></div></div><div data-wf--spacer--variant="0px" class="spacer w-variant-301f2f49-ba85-8507-11a1-c51f9e40b381"></div></div></div></header><header data-wf--section--background="base" class="section"><div class="anchor"></div><div class="padding-global"><div class="container-large"><div data-wf--spacer--variant="0px" class="spacer w-variant-301f2f49-ba85-8507-11a1-c51f9e40b381"></div><div><div data-wf--content-wrapper--variant="base" class="content-wrapper"><div data-wf--spacer--variant="0px" class="spacer w-variant-301f2f49-ba85-8507-11a1-c51f9e40b381"></div><div class="content max-width-940 margin-horizontal-auto"><div class="rich-text-wrapper"><div class="text-rich-text w-richtext"><p>Most agents, when they get into production fail because they have no persistent state, or long term memory.</p><p>A person contacts support about an SSO issue in a Kubernetes deployment and they&#x27;ve already provided the relevant context in a previous conversation: Enterprise plan, cluster environment, integration details.</p><p>The agent asks for the same information again.</p><p>Nothing is broken in the agent flow, the agent simply doesn&#x27;t remember key details across conversations. Every chat starts with an empty context window, so the model has to re-collect the same information before it can reason about the problem.</p><p>If you use LangGraph, it provides two memory mechanisms that address different layers of this problem. Most implementations only use the first, short term memory.</p><h2>The Two Memory Types</h2><div class="w-embed"><div style="overflow-x:auto;">
  <table style="width:100%; border-collapse:collapse; font-family:inherit; font-size:16px; line-height:1.5;">
    <thead>
      <tr>
        <th style="text-align:left; padding:12px 16px; border-bottom:1px solid #ddd;">Memory Type</th>
        <th style="text-align:left; padding:12px 16px; border-bottom:1px solid #ddd;">Scope</th>
        <th style="text-align:left; padding:12px 16px; border-bottom:1px solid #ddd;">Persistence</th>
        <th style="text-align:left; padding:12px 16px; border-bottom:1px solid #ddd;">Use Case</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="padding:12px 16px; border-bottom:1px solid #eee;">Checkpointer</td>
        <td style="padding:12px 16px; border-bottom:1px solid #eee;">Single thread</td>
        <td style="padding:12px 16px; border-bottom:1px solid #eee;">Thread lifetime</td>
        <td style="padding:12px 16px; border-bottom:1px solid #eee;">Conversation continuity</td>
      </tr>
      <tr>
        <td style="padding:12px 16px;">Store</td>
        <td style="padding:12px 16px;">Cross-thread</td>
        <td style="padding:12px 16px;">Indefinite</td>
        <td style="padding:12px 16px;">User preferences, facts, history</td>
      </tr>
    </tbody>
  </table>
</div></div><p>‍</p><p>Without the checkpointer, every <code>invoke</code> call is a fresh conversation. Without the Store, every new thread is a fresh relationship. You need both.</p><h2>The Architecture</h2><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-plaintext" style="white-space:pre-wrap"><span><span>                    ┌─────────────────────────────────┐
</span></span><span>                    │         InMemoryStore           │
</span><span>                    │   (&quot;memories&quot;, user_id)         │
</span><span>                    │   ┌─────────┐ ┌─────────┐       │
</span><span>                    │   │ prefs   │ │ facts   │  ...  │
</span><span>                    │   └─────────┘ └─────────┘       │
</span><span>                    └──────────┬──────────────────────┘
</span><span>                               │ search / put
</span><span>                               ▼
</span><span>[User Message] → [Load Memories] → [Agent] → [Extract &amp; Save Memories] → [Response]
</span><span>                                      │
</span><span>                                      ▼
</span><span>                              ┌───────────────┐
</span><span>                              │ InMemorySaver │
</span><span>                              │  (thread_id)  │
</span><span>                              │  checkpoint   │
</span><span>                              └───────────────┘</span></code></pre><p>‍</p><p>The checkpointer is invisible to the developer and end user. LangGraph handles it automatically when you compile with <code>checkpointer=</code>. The Store requires explicit read/write in your node functions. That asymmetry, automatic vs coded, is deliberate: conversation history is structural while long-term memory is a product decision and full of complexity.</p><h2>Short-Term Memory Persistence: The Checkpointer</h2><p>The checkpointer saves a snapshot of graph state at every super-step. Pass a <code>thread_id</code> in config, and LangGraph will restore state from the last checkpoint for that thread. No code changes to your nodes.</p><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span style="color:#dcc6e0">from</span><span> langchain_anthropic </span><span style="color:#dcc6e0">import</span><span> ChatAnthropic
</span></span><span><span></span><span style="color:#dcc6e0">from</span><span> langchain_core.messages </span><span style="color:#dcc6e0">import</span><span> HumanMessage, SystemMessage
</span></span><span><span></span><span style="color:#dcc6e0">from</span><span> langgraph.checkpoint.memory </span><span style="color:#dcc6e0">import</span><span> InMemorySaver
</span></span><span><span></span><span style="color:#dcc6e0">from</span><span> langgraph.graph </span><span style="color:#dcc6e0">import</span><span> StateGraph, START, END, MessagesState
</span></span><span><span></span><span style="color:#dcc6e0">from</span><span> langsmith </span><span style="color:#dcc6e0">import</span><span> traceable
</span></span><span>
</span><span><span>llm = ChatAnthropic(model=</span><span style="color:#abe338">&quot;claude-sonnet-4-5-20250929&quot;</span><span>, temperature=</span><span style="color:#f5ab35">0</span><span>)
</span></span><span>
</span><span>
</span><span><span></span><span style="color:#f5ab35">@traceable(</span><span style="color:#f5ab35">name=</span><span style="color:#abe338">&quot;support_agent&quot;</span><span style="color:#f5ab35">, run_type=</span><span style="color:#abe338">&quot;chain&quot;</span><span style="color:#f5ab35">)</span><span>
</span></span><span><span></span><span class="hljs-function" style="color:#dcc6e0">def</span><span class="hljs-function"> </span><span class="hljs-function" style="color:#00e0e0">call_model</span><span class="hljs-function">(</span><span class="hljs-function" style="color:#f5ab35">state: MessagesState</span><span class="hljs-function">) -&gt; </span><span class="hljs-function" style="color:#f5ab35">dict</span><span class="hljs-function">:</span><span>
</span></span><span>    response = llm.invoke([
</span><span>        SystemMessage(
</span><span><span>            content=</span><span style="color:#abe338">&quot;You are a customer support agent. Be helpful and concise. &quot;</span><span>
</span></span><span><span>                    </span><span style="color:#abe338">&quot;Reference earlier parts of the conversation when relevant.&quot;</span><span>
</span></span><span>        ),
</span><span><span>        *state[</span><span style="color:#abe338">&quot;messages&quot;</span><span>],
</span></span><span>    ])
</span><span><span>    </span><span style="color:#dcc6e0">return</span><span> {</span><span style="color:#abe338">&quot;messages&quot;</span><span>: [response]}
</span></span><span>
</span><span>
</span><span>builder = StateGraph(MessagesState)
</span><span><span>builder.add_node(</span><span style="color:#abe338">&quot;agent&quot;</span><span>, call_model)
</span></span><span><span>builder.add_edge(START, </span><span style="color:#abe338">&quot;agent&quot;</span><span>)
</span></span><span><span>builder.add_edge(</span><span style="color:#abe338">&quot;agent&quot;</span><span>, END)
</span></span><span>
</span><span>checkpointer = InMemorySaver()
</span><span><span>graph = builder.</span><span style="color:#f5ab35">compile</span><span>(checkpointer=checkpointer)</span></span></code></pre><p>Using it across turns:</p><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span>config = {</span><span style="color:#abe338">&quot;configurable&quot;</span><span>: {</span><span style="color:#abe338">&quot;thread_id&quot;</span><span>: </span><span style="color:#abe338">&quot;customer-session-42&quot;</span><span>}}
</span></span><span>
</span><span>result1 = graph.invoke(
</span><span><span>    {</span><span style="color:#abe338">&quot;messages&quot;</span><span>: [HumanMessage(content=</span><span style="color:#abe338">&quot;I&#x27;m on the Enterprise plan and my SSO is broken.&quot;</span><span>)]},
</span></span><span>    config=config,
</span><span>)
</span><span>
</span><span>result2 = graph.invoke(
</span><span><span>    {</span><span style="color:#abe338">&quot;messages&quot;</span><span>: [HumanMessage(content=</span><span style="color:#abe338">&quot;The error code is SSO-403.&quot;</span><span>)]},
</span></span><span>    config=config,
</span><span>)
</span><span><span></span><span style="color:#f5ab35">print</span><span>(result2[</span><span style="color:#abe338">&quot;messages&quot;</span><span>][-</span><span style="color:#f5ab35">1</span><span>].content)</span></span></code></pre><p>‍</p><p>The second call knows about the Enterprise plan and SSO context because the checkpointer restored the full conversation.</p><p><strong>For production, swap <code>InMemorySaver</code> for <code>PostgresSaver</code>:</strong></p><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span style="color:#dcc6e0">from</span><span> langgraph.checkpoint.postgres </span><span style="color:#dcc6e0">import</span><span> PostgresSaver
</span></span><span>
</span><span>checkpointer = PostgresSaver.from_conn_string(
</span><span><span>    </span><span style="color:#abe338">&quot;postgresql://user:pass@localhost:5432/langgraph&quot;</span><span>
</span></span><span>)</span></code></pre><p>‍</p><p><code>InMemorySaver</code> is a dictionary, so it disappears when the process dies. This is fine for development and tests. We like <code>PostgresSaver</code> for production.</p><h2>Long-Term Memory for Stateful Agents: The Store</h2><p>The checkpointer solves session continuity while the <code>Store</code> solves <em>relationship</em> continuity. A returning customer opens a new thread, or new converstion with different <code>thread_id</code>, the agent should still knows their setup.</p><p>The Store organizes memories as JSON documents under namespaces. Think of namespaces as directories: <code>(&quot;memories&quot;, &quot;user-123&quot;)</code> scopes all memories to a specific user. Each memory has a key (like a filename) and a value (any JSON-serializable dict).</p><p>‍</p><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span style="color:#dcc6e0">import</span><span> uuid
</span></span><span>
</span><span><span></span><span style="color:#dcc6e0">from</span><span> langgraph.checkpoint.memory </span><span style="color:#dcc6e0">import</span><span> InMemorySaver
</span></span><span><span></span><span style="color:#dcc6e0">from</span><span> langgraph.store.memory </span><span style="color:#dcc6e0">import</span><span> InMemoryStore
</span></span><span><span></span><span style="color:#dcc6e0">from</span><span> langgraph.graph </span><span style="color:#dcc6e0">import</span><span> StateGraph, START, END, MessagesState
</span></span><span><span></span><span style="color:#dcc6e0">from</span><span> langchain_anthropic </span><span style="color:#dcc6e0">import</span><span> ChatAnthropic
</span></span><span><span></span><span style="color:#dcc6e0">from</span><span> langchain_core.messages </span><span style="color:#dcc6e0">import</span><span> HumanMessage, SystemMessage
</span></span><span><span></span><span style="color:#dcc6e0">from</span><span> langsmith </span><span style="color:#dcc6e0">import</span><span> traceable
</span></span><span>
</span><span><span>llm = ChatAnthropic(model=</span><span style="color:#abe338">&quot;claude-sonnet-4-6&quot;</span><span>, temperature=</span><span style="color:#f5ab35">0</span><span>)
</span></span><span>
</span><span>store = InMemoryStore()
</span><span>checkpointer = InMemorySaver()</span></code></pre><p>‍</p><h3>Saving Memories</h3><p>After the agent responds, extract useful facts and persist them. The extraction step is an LLM call, you&#x27;re asking the model to identify what&#x27;s worth remembering.</p><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span style="color:#f5ab35">@traceable(</span><span style="color:#f5ab35">name=</span><span style="color:#abe338">&quot;extract_memories&quot;</span><span style="color:#f5ab35">, run_type=</span><span style="color:#abe338">&quot;chain&quot;</span><span style="color:#f5ab35">)</span><span>
</span></span><span><span></span><span class="hljs-function" style="color:#dcc6e0">def</span><span class="hljs-function"> </span><span class="hljs-function" style="color:#00e0e0">extract_and_save_memories</span><span class="hljs-function">(</span><span class="hljs-function" style="color:#f5ab35">state: MessagesState, store, config</span><span class="hljs-function">) -&gt; </span><span class="hljs-function" style="color:#f5ab35">dict</span><span class="hljs-function">:</span><span>
</span></span><span><span>    user_id = config[</span><span style="color:#abe338">&quot;configurable&quot;</span><span>].get(</span><span style="color:#abe338">&quot;user_id&quot;</span><span>, </span><span style="color:#abe338">&quot;anonymous&quot;</span><span>)
</span></span><span><span>    namespace = (</span><span style="color:#abe338">&quot;memories&quot;</span><span>, user_id)
</span></span><span>
</span><span><span>    conversation = </span><span style="color:#abe338">&quot;\n&quot;</span><span>.join(
</span></span><span><span>        </span><span style="color:#abe338">f&quot;</span><span class="hljs-subst" style="color:#abe338">{m.</span><span class="hljs-subst" style="color:#f5ab35">type</span><span class="hljs-subst" style="color:#abe338">}</span><span style="color:#abe338">: </span><span class="hljs-subst" style="color:#abe338">{m.content}</span><span style="color:#abe338">&quot;</span><span> </span><span style="color:#dcc6e0">for</span><span> m </span><span style="color:#dcc6e0">in</span><span> state[</span><span style="color:#abe338">&quot;messages&quot;</span><span>][-</span><span style="color:#f5ab35">4</span><span>:]
</span></span><span>    )
</span><span>
</span><span>    extraction = llm.invoke([
</span><span>        SystemMessage(
</span><span><span>            content=</span><span style="color:#abe338">&quot;Extract key facts about this user from the conversation. &quot;</span><span>
</span></span><span><span>                    </span><span style="color:#abe338">&quot;Return each fact on its own line. Only extract concrete, &quot;</span><span>
</span></span><span><span>                    </span><span style="color:#abe338">&quot;reusable facts (plan type, tech stack, preferences, issues). &quot;</span><span>
</span></span><span><span>                    </span><span style="color:#abe338">&quot;If there are no new facts, respond with NONE.&quot;</span><span>
</span></span><span>        ),
</span><span><span>        HumanMessage(content=</span><span style="color:#abe338">f&quot;Conversation:\n</span><span class="hljs-subst" style="color:#abe338">{conversation}</span><span style="color:#abe338">&quot;</span><span>),
</span></span><span>    ])
</span><span>
</span><span><span>    </span><span style="color:#dcc6e0">if</span><span> </span><span style="color:#abe338">&quot;NONE&quot;</span><span> </span><span style="color:#dcc6e0">not</span><span> </span><span style="color:#dcc6e0">in</span><span> extraction.content.upper():
</span></span><span><span>        facts = [f.strip() </span><span style="color:#dcc6e0">for</span><span> f </span><span style="color:#dcc6e0">in</span><span> extraction.content.strip().split(</span><span style="color:#abe338">&quot;\n&quot;</span><span>) </span><span style="color:#dcc6e0">if</span><span> f.strip()]
</span></span><span><span>        </span><span style="color:#dcc6e0">for</span><span> fact </span><span style="color:#dcc6e0">in</span><span> facts:
</span></span><span><span>            memory_id = </span><span style="color:#f5ab35">str</span><span>(uuid.uuid4())
</span></span><span><span>            store.put(namespace, memory_id, {</span><span style="color:#abe338">&quot;memory&quot;</span><span>: fact})
</span></span><span>
</span><span><span>    </span><span style="color:#dcc6e0">return</span><span> state</span></span></code></pre><p>‍</p><h3>Loading Memories</h3><p>Before the agent responds, search the Store for relevant memories and inject them into the system prompt.</p><p>‍</p><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span style="color:#f5ab35">@traceable(</span><span style="color:#f5ab35">name=</span><span style="color:#abe338">&quot;load_memories&quot;</span><span style="color:#f5ab35">, run_type=</span><span style="color:#abe338">&quot;chain&quot;</span><span style="color:#f5ab35">)</span><span>
</span></span><span><span></span><span class="hljs-function" style="color:#dcc6e0">def</span><span class="hljs-function"> </span><span class="hljs-function" style="color:#00e0e0">load_memories</span><span class="hljs-function">(</span><span class="hljs-function" style="color:#f5ab35">state: MessagesState, store, config</span><span class="hljs-function">) -&gt; </span><span class="hljs-function" style="color:#f5ab35">dict</span><span class="hljs-function">:</span><span>
</span></span><span><span>    user_id = config[</span><span style="color:#abe338">&quot;configurable&quot;</span><span>].get(</span><span style="color:#abe338">&quot;user_id&quot;</span><span>, </span><span style="color:#abe338">&quot;anonymous&quot;</span><span>)
</span></span><span><span>    namespace = (</span><span style="color:#abe338">&quot;memories&quot;</span><span>, user_id)
</span></span><span>
</span><span><span>    memories = store.search(namespace, limit=</span><span style="color:#f5ab35">10</span><span>)
</span></span><span><span>    memory_text = </span><span style="color:#abe338">&quot;\n&quot;</span><span>.join(</span><span style="color:#abe338">f&quot;- </span><span class="hljs-subst" style="color:#abe338">{m.value[</span><span class="hljs-subst" style="color:#abe338">&#x27;memory&#x27;</span><span class="hljs-subst" style="color:#abe338">]}</span><span style="color:#abe338">&quot;</span><span> </span><span style="color:#dcc6e0">for</span><span> m </span><span style="color:#dcc6e0">in</span><span> memories)
</span></span><span>
</span><span><span>    </span><span style="color:#dcc6e0">if</span><span> memory_text:
</span></span><span>        system_msg = SystemMessage(
</span><span><span>            content=</span><span style="color:#abe338">f&quot;You are a customer support agent. Be helpful and concise.\n\n&quot;</span><span>
</span></span><span><span>                    </span><span style="color:#abe338">f&quot;Known facts about this customer:\n</span><span class="hljs-subst" style="color:#abe338">{memory_text}</span><span style="color:#abe338">\n\n&quot;</span><span>
</span></span><span><span>                    </span><span style="color:#abe338">f&quot;Use these facts to personalize your response. &quot;</span><span>
</span></span><span><span>                    </span><span style="color:#abe338">f&quot;Do not ask the customer to re-explain information you already know.&quot;</span><span>
</span></span><span>        )
</span><span><span>    </span><span style="color:#dcc6e0">else</span><span>:
</span></span><span>        system_msg = SystemMessage(
</span><span><span>            content=</span><span style="color:#abe338">&quot;You are a customer support agent. Be helpful and concise.&quot;</span><span>
</span></span><span>        )
</span><span>
</span><span><span>    </span><span style="color:#dcc6e0">return</span><span> {</span><span style="color:#abe338">&quot;messages&quot;</span><span>: [system_msg] + state[</span><span style="color:#abe338">&quot;messages&quot;</span><span>]}
</span></span><span>
</span><span>
</span><span><span></span><span style="color:#f5ab35">@traceable(</span><span style="color:#f5ab35">name=</span><span style="color:#abe338">&quot;support_agent&quot;</span><span style="color:#f5ab35">, run_type=</span><span style="color:#abe338">&quot;chain&quot;</span><span style="color:#f5ab35">)</span><span>
</span></span><span><span></span><span class="hljs-function" style="color:#dcc6e0">def</span><span class="hljs-function"> </span><span class="hljs-function" style="color:#00e0e0">call_model</span><span class="hljs-function">(</span><span class="hljs-function" style="color:#f5ab35">state: MessagesState</span><span class="hljs-function">) -&gt; </span><span class="hljs-function" style="color:#f5ab35">dict</span><span class="hljs-function">:</span><span>
</span></span><span><span>    response = llm.invoke(state[</span><span style="color:#abe338">&quot;messages&quot;</span><span>])
</span></span><span><span>    </span><span style="color:#dcc6e0">return</span><span> {</span><span style="color:#abe338">&quot;messages&quot;</span><span>: [response]}</span></span></code></pre><p>‍</p><h3>Graph Assembly</h3><p>Wire it together: load memories, call the agent, extract and save new memories.</p><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span>builder = StateGraph(MessagesState)
</span></span><span><span>builder.add_node(</span><span style="color:#abe338">&quot;load_memories&quot;</span><span>, load_memories)
</span></span><span><span>builder.add_node(</span><span style="color:#abe338">&quot;agent&quot;</span><span>, call_model)
</span></span><span><span>builder.add_node(</span><span style="color:#abe338">&quot;save_memories&quot;</span><span>, extract_and_save_memories)
</span></span><span>
</span><span><span>builder.add_edge(START, </span><span style="color:#abe338">&quot;load_memories&quot;</span><span>)
</span></span><span><span>builder.add_edge(</span><span style="color:#abe338">&quot;load_memories&quot;</span><span>, </span><span style="color:#abe338">&quot;agent&quot;</span><span>)
</span></span><span><span>builder.add_edge(</span><span style="color:#abe338">&quot;agent&quot;</span><span>, </span><span style="color:#abe338">&quot;save_memories&quot;</span><span>)
</span></span><span><span>builder.add_edge(</span><span style="color:#abe338">&quot;save_memories&quot;</span><span>, END)
</span></span><span>
</span><span><span>graph = builder.</span><span style="color:#f5ab35">compile</span><span>(checkpointer=checkpointer, store=store)</span></span></code></pre><p>‍</p><h3>Cross-Thread Memory in Action</h3><p>Watch the agent remember across completely separate conversations:</p><p>‍</p><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span>config_thread_1 = {
</span></span><span><span>    </span><span style="color:#abe338">&quot;configurable&quot;</span><span>: {</span><span style="color:#abe338">&quot;thread_id&quot;</span><span>: </span><span style="color:#abe338">&quot;session-1&quot;</span><span>, </span><span style="color:#abe338">&quot;user_id&quot;</span><span>: </span><span style="color:#abe338">&quot;user-42&quot;</span><span>}
</span></span><span>}
</span><span>
</span><span>result1 = graph.invoke(
</span><span><span>    {</span><span style="color:#abe338">&quot;messages&quot;</span><span>: [HumanMessage(
</span></span><span><span>        content=</span><span style="color:#abe338">&quot;Hi, I&#x27;m on the Enterprise plan. We run Kubernetes &quot;</span><span>
</span></span><span><span>                </span><span style="color:#abe338">&quot;on AWS and we&#x27;re having trouble with SSO integration.&quot;</span><span>
</span></span><span>    )]},
</span><span>    config=config_thread_1,
</span><span>)
</span><span><span></span><span style="color:#f5ab35">print</span><span>(</span><span style="color:#abe338">&quot;Thread 1:&quot;</span><span>, result1[</span><span style="color:#abe338">&quot;messages&quot;</span><span>][-</span><span style="color:#f5ab35">1</span><span>].content[:</span><span style="color:#f5ab35">200</span><span>])
</span></span><span>
</span><span>config_thread_2 = {
</span><span><span>    </span><span style="color:#abe338">&quot;configurable&quot;</span><span>: {</span><span style="color:#abe338">&quot;thread_id&quot;</span><span>: </span><span style="color:#abe338">&quot;session-2&quot;</span><span>, </span><span style="color:#abe338">&quot;user_id&quot;</span><span>: </span><span style="color:#abe338">&quot;user-42&quot;</span><span>}
</span></span><span>}
</span><span>
</span><span>result2 = graph.invoke(
</span><span><span>    {</span><span style="color:#abe338">&quot;messages&quot;</span><span>: [HumanMessage(
</span></span><span><span>        content=</span><span style="color:#abe338">&quot;Hey, I have a question about scaling our deployment.&quot;</span><span>
</span></span><span>    )]},
</span><span>    config=config_thread_2,
</span><span>)
</span><span><span></span><span style="color:#f5ab35">print</span><span>(</span><span style="color:#abe338">&quot;Thread 2:&quot;</span><span>, result2[</span><span style="color:#abe338">&quot;messages&quot;</span><span>][-</span><span style="color:#f5ab35">1</span><span>].content[:</span><span style="color:#f5ab35">200</span><span>])</span></span></code></pre><p>‍</p><p>In thread 2, the agent already knows the customer is on Enterprise, running Kubernetes on AWS. No re-asking. The memory came from the Store, scoped to <code>user-42</code>, not from the checkpointer (which only holds thread 1&#x27;s conversation).</p><p><strong>For production, swap <code>InMemoryStore</code> for <code>PostgresStore</code>:<br/>‍</strong></p><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span style="color:#dcc6e0">from</span><span> langgraph.store.postgres </span><span style="color:#dcc6e0">import</span><span> PostgresStore
</span></span><span>
</span><span>store = PostgresStore.from_conn_string(
</span><span><span>    </span><span style="color:#abe338">&quot;postgresql://user:pass@localhost:5432/langgraph&quot;</span><span>
</span></span><span>)</span></code></pre><p>‍</p><h2>Memory with Semantic Search</h2><p>Flat <code>store.search()</code> returns all memories in a namespace up to the limit. That works fine when a user has 5 memories. At 500, you&#x27;re stuffing irrelevant facts into the context window and paying for tokens that hurt more than they help.</p><p><code>InMemoryStore</code> supports an <code>index</code> parameter for semantic search. Pass an embedding function and the store will rank memories by relevance to the current query:</p><p>‍</p><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span style="color:#dcc6e0">from</span><span> langchain_openai </span><span style="color:#dcc6e0">import</span><span> OpenAIEmbeddings
</span></span><span>
</span><span><span>embeddings = OpenAIEmbeddings(model=</span><span style="color:#abe338">&quot;text-embedding-3-small&quot;</span><span>)
</span></span><span>
</span><span>store = InMemoryStore(
</span><span>    index={
</span><span><span>        </span><span style="color:#abe338">&quot;embed&quot;</span><span>: embeddings,
</span></span><span><span>        </span><span style="color:#abe338">&quot;dims&quot;</span><span>: </span><span style="color:#f5ab35">1536</span><span>,
</span></span><span><span>        </span><span style="color:#abe338">&quot;fields&quot;</span><span>: [</span><span style="color:#abe338">&quot;memory&quot;</span><span>],
</span></span><span>    }
</span><span>)</span></code></pre><p>‍</p><p>Now <code>store.search()</code> accepts a <code>query</code> parameter:</p><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span style="color:#f5ab35">@traceable(</span><span style="color:#f5ab35">name=</span><span style="color:#abe338">&quot;load_memories_semantic&quot;</span><span style="color:#f5ab35">, run_type=</span><span style="color:#abe338">&quot;chain&quot;</span><span style="color:#f5ab35">)</span><span>
</span></span><span><span></span><span class="hljs-function" style="color:#dcc6e0">def</span><span class="hljs-function"> </span><span class="hljs-function" style="color:#00e0e0">load_memories</span><span class="hljs-function">(</span><span class="hljs-function" style="color:#f5ab35">state: MessagesState, store, config</span><span class="hljs-function">) -&gt; </span><span class="hljs-function" style="color:#f5ab35">dict</span><span class="hljs-function">:</span><span>
</span></span><span><span>    user_id = config[</span><span style="color:#abe338">&quot;configurable&quot;</span><span>].get(</span><span style="color:#abe338">&quot;user_id&quot;</span><span>, </span><span style="color:#abe338">&quot;anonymous&quot;</span><span>)
</span></span><span><span>    namespace = (</span><span style="color:#abe338">&quot;memories&quot;</span><span>, user_id)
</span></span><span>
</span><span><span>    last_message = state[</span><span style="color:#abe338">&quot;messages&quot;</span><span>][-</span><span style="color:#f5ab35">1</span><span>].content
</span></span><span><span>    memories = store.search(namespace, query=last_message, limit=</span><span style="color:#f5ab35">5</span><span>)
</span></span><span>
</span><span><span>    memory_text = </span><span style="color:#abe338">&quot;\n&quot;</span><span>.join(</span><span style="color:#abe338">f&quot;- </span><span class="hljs-subst" style="color:#abe338">{m.value[</span><span class="hljs-subst" style="color:#abe338">&#x27;memory&#x27;</span><span class="hljs-subst" style="color:#abe338">]}</span><span style="color:#abe338">&quot;</span><span> </span><span style="color:#dcc6e0">for</span><span> m </span><span style="color:#dcc6e0">in</span><span> memories)
</span></span><span>
</span><span><span>    </span><span style="color:#dcc6e0">if</span><span> memory_text:
</span></span><span>        system_msg = SystemMessage(
</span><span><span>            content=</span><span style="color:#abe338">f&quot;You are a customer support agent. Be helpful and concise.\n\n&quot;</span><span>
</span></span><span><span>                    </span><span style="color:#abe338">f&quot;Relevant facts about this customer:\n</span><span class="hljs-subst" style="color:#abe338">{memory_text}</span><span style="color:#abe338">\n\n&quot;</span><span>
</span></span><span><span>                    </span><span style="color:#abe338">f&quot;Use these facts to personalize your response.&quot;</span><span>
</span></span><span>        )
</span><span><span>    </span><span style="color:#dcc6e0">else</span><span>:
</span></span><span>        system_msg = SystemMessage(
</span><span><span>            content=</span><span style="color:#abe338">&quot;You are a customer support agent. Be helpful and concise.&quot;</span><span>
</span></span><span>        )
</span><span>
</span><span><span>    </span><span style="color:#dcc6e0">return</span><span> {</span><span style="color:#abe338">&quot;messages&quot;</span><span>: [system_msg] + state[</span><span style="color:#abe338">&quot;messages&quot;</span><span>]}</span></span></code></pre><p>‍</p><p>The difference: when the customer asks about billing, you pull billing-related memories instead of their entire history. Fewer tokens, more relevant context, better responses.</p><h2>Production Failures</h2><p>These are the failures that show up after memory has been running in production for a few weeks.</p><p><strong>1. Memory Bloat.</strong> The extraction node saves a new memory for every turn. After 50 conversations, user-42 has 300 memories, half of them redundant (&quot;User is on Enterprise plan&quot; saved 12 times). Token costs climb, context window fills with repetitive facts, and response quality actually <em>decreases</em>. Fix: deduplicate before saving. Check if a semantically similar memory already exists:</p><p>‍</p><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span style="color:#f5ab35">@traceable(</span><span style="color:#f5ab35">name=</span><span style="color:#abe338">&quot;deduplicated_save&quot;</span><span style="color:#f5ab35">, run_type=</span><span style="color:#abe338">&quot;chain&quot;</span><span style="color:#f5ab35">)</span><span>
</span></span><span><span></span><span class="hljs-function" style="color:#dcc6e0">def</span><span class="hljs-function"> </span><span class="hljs-function" style="color:#00e0e0">save_memory_deduped</span><span class="hljs-function">(</span><span class="hljs-function" style="color:#f5ab35">store, namespace: </span><span class="hljs-function" style="color:#f5ab35">tuple</span><span class="hljs-function" style="color:#f5ab35">, fact: </span><span class="hljs-function" style="color:#f5ab35">str</span><span class="hljs-function">) -&gt; </span><span class="hljs-function" style="color:#f5ab35">bool</span><span class="hljs-function">:</span><span>
</span></span><span><span>    existing = store.search(namespace, query=fact, limit=</span><span style="color:#f5ab35">3</span><span>)
</span></span><span><span>    </span><span style="color:#dcc6e0">for</span><span> mem </span><span style="color:#dcc6e0">in</span><span> existing:
</span></span><span><span>        </span><span style="color:#dcc6e0">if</span><span> mem.value[</span><span style="color:#abe338">&quot;memory&quot;</span><span>].lower().strip() == fact.lower().strip():
</span></span><span><span>            </span><span style="color:#dcc6e0">return</span><span> </span><span style="color:#f5ab35">False</span><span>
</span></span><span><span>    memory_id = </span><span style="color:#f5ab35">str</span><span>(uuid.uuid4())
</span></span><span><span>    store.put(namespace, memory_id, {</span><span style="color:#abe338">&quot;memory&quot;</span><span>: fact})
</span></span><span><span>    </span><span style="color:#dcc6e0">return</span><span> </span><span style="color:#f5ab35">True</span></span></code></pre><p>‍</p><p><strong>2. Stale Memories.</strong> The customer upgraded from Pro to Enterprise two months ago. Both facts are in the Store. The agent says &quot;As a Pro customer...&quot; — a worse experience than having no memory at all. Fix: timestamp your memories and either overwrite by category or implement a TTL sweep:<br/>‍</p><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span style="color:#dcc6e0">from</span><span> datetime </span><span style="color:#dcc6e0">import</span><span> datetime, timezone
</span></span><span>
</span><span><span>store.put(namespace, </span><span style="color:#abe338">&quot;plan-type&quot;</span><span>, {
</span></span><span><span>    </span><span style="color:#abe338">&quot;memory&quot;</span><span>: </span><span style="color:#abe338">&quot;Customer is on Enterprise plan&quot;</span><span>,
</span></span><span><span>    </span><span style="color:#abe338">&quot;category&quot;</span><span>: </span><span style="color:#abe338">&quot;plan&quot;</span><span>,
</span></span><span><span>    </span><span style="color:#abe338">&quot;updated_at&quot;</span><span>: datetime.now(timezone.utc).isoformat(),
</span></span><span>})</span></code></pre><p>‍</p><p>Using a deterministic key like <code>&quot;plan-type&quot;</code> instead of a UUID means the next update overwrites the old value. Category-based keys are the simplest fix for facts that change.</p><p><strong>3. Namespace Collisions.</strong> Two systems write memories for the same user under different namespace conventions — one uses <code>(&quot;memories&quot;, user_id)</code>, the other uses <code>(&quot;user_data&quot;, user_id)</code>. Neither system sees the other&#x27;s data. There&#x27;s no error — just incomplete context. Fix: document your namespace convention in an ADR and enforce it with a helper function:</p><p>‍</p><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span class="hljs-function" style="color:#dcc6e0">def</span><span class="hljs-function"> </span><span class="hljs-function" style="color:#00e0e0">user_namespace</span><span class="hljs-function">(</span><span class="hljs-function" style="color:#f5ab35">user_id: </span><span class="hljs-function" style="color:#f5ab35">str</span><span class="hljs-function">) -&gt; </span><span class="hljs-function" style="color:#f5ab35">tuple</span><span class="hljs-function">:</span><span>
</span></span><span><span>    </span><span style="color:#dcc6e0">return</span><span> (</span><span style="color:#abe338">&quot;memories&quot;</span><span>, user_id)</span></span></code></pre><p>‍</p><p><strong>4. Memory Extraction Hallucination.</strong> The extraction LLM invents facts that weren&#x27;t in the conversation. The customer mentions &quot;we&#x27;re considering Kubernetes&quot; and the extraction saves &quot;Customer runs Kubernetes in production.&quot; Once that fact is in the Store, the agent references it confidently, and now you have a support interaction based on false premises. Fix: use structured output for extraction and add a confidence threshold:</p><p>‍</p><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span style="color:#dcc6e0">from</span><span> pydantic </span><span style="color:#dcc6e0">import</span><span> BaseModel, Field
</span></span><span>
</span><span>
</span><span><span></span><span class="hljs-class" style="color:#dcc6e0">class</span><span class="hljs-class"> </span><span class="hljs-class" style="color:#00e0e0">ExtractedFact</span><span class="hljs-class">(</span><span class="hljs-class" style="color:#f5ab35">BaseModel</span><span class="hljs-class">):</span><span>
</span></span><span><span>    fact: </span><span style="color:#f5ab35">str</span><span> = Field(description=</span><span style="color:#abe338">&quot;A concrete fact stated by the user&quot;</span><span>)
</span></span><span><span>    confidence: </span><span style="color:#f5ab35">float</span><span> = Field(description=</span><span style="color:#abe338">&quot;0.0-1.0 confidence this fact is accurate&quot;</span><span>)
</span></span><span>
</span><span>
</span><span><span></span><span class="hljs-class" style="color:#dcc6e0">class</span><span class="hljs-class"> </span><span class="hljs-class" style="color:#00e0e0">ExtractionResult</span><span class="hljs-class">(</span><span class="hljs-class" style="color:#f5ab35">BaseModel</span><span class="hljs-class">):</span><span>
</span></span><span><span>    facts: </span><span style="color:#f5ab35">list</span><span>[ExtractedFact] = Field(default_factory=</span><span style="color:#f5ab35">list</span><span>)
</span></span><span>
</span><span>
</span><span>structured_llm = llm.with_structured_output(ExtractionResult)</span></code></pre><p>‍</p><p>Only save facts with confidence above 0.8. You&#x27;ll miss some, but you won&#x27;t fabricate any.</p><h2>Observability</h2><p>Memory operations are invisible without tracing. The <code>@traceable</code> decorator on <code>load_memories</code> and <code>extract_and_save_memories</code> gives you per-node spans in LangSmith. Tag traces with the user_id for filtering:</p><p>‍</p><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span style="color:#dcc6e0">from</span><span> langsmith </span><span style="color:#dcc6e0">import</span><span> tracing_context
</span></span><span>
</span><span><span></span><span style="color:#dcc6e0">with</span><span> tracing_context(
</span></span><span><span>    metadata={</span><span style="color:#abe338">&quot;user_id&quot;</span><span>: </span><span style="color:#abe338">&quot;user-42&quot;</span><span>, </span><span style="color:#abe338">&quot;memory_count&quot;</span><span>: </span><span style="color:#f5ab35">15</span><span>},
</span></span><span><span>    tags=[</span><span style="color:#abe338">&quot;production&quot;</span><span>, </span><span style="color:#abe338">&quot;memory-v2&quot;</span><span>],
</span></span><span>):
</span><span>    result = graph.invoke(
</span><span><span>        {</span><span style="color:#abe338">&quot;messages&quot;</span><span>: [HumanMessage(content=</span><span style="color:#abe338">&quot;What&#x27;s the status of my SSO issue?&quot;</span><span>)]},
</span></span><span><span>        config={</span><span style="color:#abe338">&quot;configurable&quot;</span><span>: {</span><span style="color:#abe338">&quot;thread_id&quot;</span><span>: </span><span style="color:#abe338">&quot;session-5&quot;</span><span>, </span><span style="color:#abe338">&quot;user_id&quot;</span><span>: </span><span style="color:#abe338">&quot;user-42&quot;</span><span>}},
</span></span><span>    )</span></code></pre><p>‍</p><p>The three things to watch in LangSmith:</p><ol role="list"><li><strong>Memory load latency</strong> — if <code>load_memories</code> is slow, your Store query is the bottleneck. Semantic search with large namespaces will do this.</li><li><strong>Extraction quality</strong> — open the <code>extract_memories</code> span and read the output. If you see hallucinated facts, tighten the extraction prompt or add structured output.</li><li><strong>Memory count per user</strong> — if it&#x27;s growing linearly with conversations, you&#x27;re not deduplicating.</li></ol><h2>Evals</h2><p>Memory systems need two types of evaluation: does the agent <em>recall</em> stored information, and does the agent <em>correctly use</em> that information? Shipping without these evals means memory bugs are invisible until a customer complains.</p><p>‍</p><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span style="color:#dcc6e0">from</span><span> langsmith </span><span style="color:#dcc6e0">import</span><span> Client
</span></span><span>
</span><span>ls_client = Client()
</span><span>
</span><span>dataset = ls_client.create_dataset(
</span><span><span>    dataset_name=</span><span style="color:#abe338">&quot;memory-persistence-evals&quot;</span><span>,
</span></span><span><span>    description=</span><span style="color:#abe338">&quot;Evaluates cross-thread memory recall and usage&quot;</span><span>,
</span></span><span>)
</span><span>
</span><span>ls_client.create_examples(
</span><span><span>    dataset_id=dataset.</span><span style="color:#f5ab35">id</span><span>,
</span></span><span>    inputs=[
</span><span>        {
</span><span><span>            </span><span style="color:#abe338">&quot;setup_messages&quot;</span><span>: [
</span></span><span><span>                </span><span style="color:#abe338">&quot;I&#x27;m on the Enterprise plan running Kubernetes on AWS.&quot;</span><span>,
</span></span><span><span>                </span><span style="color:#abe338">&quot;My preferred contact method is Slack.&quot;</span><span>,
</span></span><span>            ],
</span><span><span>            </span><span style="color:#abe338">&quot;test_question&quot;</span><span>: </span><span style="color:#abe338">&quot;Can you help me scale my deployment?&quot;</span><span>,
</span></span><span><span>            </span><span style="color:#abe338">&quot;user_id&quot;</span><span>: </span><span style="color:#abe338">&quot;eval-user-1&quot;</span><span>,
</span></span><span>        },
</span><span>        {
</span><span><span>            </span><span style="color:#abe338">&quot;setup_messages&quot;</span><span>: [
</span></span><span><span>                </span><span style="color:#abe338">&quot;We use PostgreSQL 15 and our database is hosted on RDS.&quot;</span><span>,
</span></span><span>            ],
</span><span><span>            </span><span style="color:#abe338">&quot;test_question&quot;</span><span>: </span><span style="color:#abe338">&quot;I&#x27;m seeing slow queries. Any suggestions?&quot;</span><span>,
</span></span><span><span>            </span><span style="color:#abe338">&quot;user_id&quot;</span><span>: </span><span style="color:#abe338">&quot;eval-user-2&quot;</span><span>,
</span></span><span>        },
</span><span>        {
</span><span><span>            </span><span style="color:#abe338">&quot;setup_messages&quot;</span><span>: [
</span></span><span><span>                </span><span style="color:#abe338">&quot;I&#x27;m on the Pro plan. I prefer detailed, technical explanations.&quot;</span><span>,
</span></span><span>            ],
</span><span><span>            </span><span style="color:#abe338">&quot;test_question&quot;</span><span>: </span><span style="color:#abe338">&quot;How do I configure SSO?&quot;</span><span>,
</span></span><span><span>            </span><span style="color:#abe338">&quot;user_id&quot;</span><span>: </span><span style="color:#abe338">&quot;eval-user-3&quot;</span><span>,
</span></span><span>        },
</span><span>    ],
</span><span>    outputs=[
</span><span><span>        {</span><span style="color:#abe338">&quot;must_recall&quot;</span><span>: [</span><span style="color:#abe338">&quot;Enterprise&quot;</span><span>, </span><span style="color:#abe338">&quot;Kubernetes&quot;</span><span>, </span><span style="color:#abe338">&quot;AWS&quot;</span><span>]},
</span></span><span><span>        {</span><span style="color:#abe338">&quot;must_recall&quot;</span><span>: [</span><span style="color:#abe338">&quot;PostgreSQL&quot;</span><span>, </span><span style="color:#abe338">&quot;RDS&quot;</span><span>]},
</span></span><span><span>        {</span><span style="color:#abe338">&quot;must_recall&quot;</span><span>: [</span><span style="color:#abe338">&quot;Pro&quot;</span><span>, </span><span style="color:#abe338">&quot;technical&quot;</span><span>]},
</span></span><span>    ],
</span><span>)</span></code></pre><pre contenteditable="false" class="w-code-block" style="display:block;overflow-x:auto;background:#2b2b2b;color:#f8f8f2;padding:0.5em"><code class="language-python" style="white-space:pre-wrap"><span><span style="color:#dcc6e0">from</span><span> langsmith </span><span style="color:#dcc6e0">import</span><span> evaluate
</span></span><span><span></span><span style="color:#dcc6e0">from</span><span> openevals.llm </span><span style="color:#dcc6e0">import</span><span> create_llm_as_judge
</span></span><span>
</span><span><span>MEMORY_QUALITY_PROMPT = </span><span style="color:#abe338">&quot;&quot;&quot;\
</span></span><span>The user previously told the agent the following facts:
</span><span>{inputs[setup_messages]}
</span><span>
</span><span>The user then asked (in a NEW conversation thread):
</span><span>{inputs[test_question]}
</span><span>
</span><span>The agent responded:
</span><span>{outputs[response]}
</span><span>
</span><span>Rate 0.0-1.0 on whether the agent correctly recalled and used the stored facts.
</span><span>A score of 1.0 means the agent referenced all relevant prior facts naturally.
</span><span>A score of 0.0 means the agent showed no awareness of prior interactions.
</span><span><span style="color:#abe338">Return ONLY: {{&quot;score&quot;: &lt;float&gt;, &quot;reasoning&quot;: &quot;&lt;explanation&gt;&quot;}}&quot;&quot;&quot;</span><span>
</span></span><span>
</span><span>memory_judge = create_llm_as_judge(
</span><span>    prompt=MEMORY_QUALITY_PROMPT,
</span><span><span>    model=</span><span style="color:#abe338">&quot;anthropic:claude-sonnet-4-5-20250929&quot;</span><span>,
</span></span><span><span>    feedback_key=</span><span style="color:#abe338">&quot;memory_quality&quot;</span><span>,
</span></span><span>)
</span><span>
</span><span>
</span><span><span></span><span class="hljs-function" style="color:#dcc6e0">def</span><span class="hljs-function"> </span><span class="hljs-function" style="color:#00e0e0">memory_recall</span><span class="hljs-function">(</span><span class="hljs-function" style="color:#f5ab35">inputs: </span><span class="hljs-function" style="color:#f5ab35">dict</span><span class="hljs-function" style="color:#f5ab35">, outputs: </span><span class="hljs-function" style="color:#f5ab35">dict</span><span class="hljs-function" style="color:#f5ab35">, reference_outputs: </span><span class="hljs-function" style="color:#f5ab35">dict</span><span class="hljs-function">) -&gt; </span><span class="hljs-function" style="color:#f5ab35">dict</span><span class="hljs-function">:</span><span>
</span></span><span><span>    </span><span style="color:#abe338">&quot;&quot;&quot;Check if specific facts were recalled in the response.&quot;&quot;&quot;</span><span>
</span></span><span><span>    response_text = outputs.get(</span><span style="color:#abe338">&quot;response&quot;</span><span>, </span><span style="color:#abe338">&quot;&quot;</span><span>).lower()
</span></span><span><span>    must_recall = reference_outputs.get(</span><span style="color:#abe338">&quot;must_recall&quot;</span><span>, [])
</span></span><span><span>    hits = </span><span style="color:#f5ab35">sum</span><span>(</span><span style="color:#f5ab35">1</span><span> </span><span style="color:#dcc6e0">for</span><span> term </span><span style="color:#dcc6e0">in</span><span> must_recall </span><span style="color:#dcc6e0">if</span><span> term.lower() </span><span style="color:#dcc6e0">in</span><span> response_text)
</span></span><span><span>    </span><span style="color:#dcc6e0">return</span><span> {
</span></span><span><span>        </span><span style="color:#abe338">&quot;key&quot;</span><span>: </span><span style="color:#abe338">&quot;memory_recall&quot;</span><span>,
</span></span><span><span>        </span><span style="color:#abe338">&quot;score&quot;</span><span>: hits / </span><span style="color:#f5ab35">len</span><span>(must_recall) </span><span style="color:#dcc6e0">if</span><span> must_recall </span><span style="color:#dcc6e0">else</span><span> </span><span style="color:#f5ab35">1.0</span><span>,
</span></span><span>    }
</span><span>
</span><span>
</span><span><span></span><span class="hljs-function" style="color:#dcc6e0">def</span><span class="hljs-function"> </span><span class="hljs-function" style="color:#00e0e0">target</span><span class="hljs-function">(</span><span class="hljs-function" style="color:#f5ab35">inputs: </span><span class="hljs-function" style="color:#f5ab35">dict</span><span class="hljs-function">) -&gt; </span><span class="hljs-function" style="color:#f5ab35">dict</span><span class="hljs-function">:</span><span>
</span></span><span>    test_store = InMemoryStore()
</span><span>    test_checkpointer = InMemorySaver()
</span><span>
</span><span><span>    test_graph = builder.</span><span style="color:#f5ab35">compile</span><span>(checkpointer=test_checkpointer, store=test_store)
</span></span><span>
</span><span><span>    user_id = inputs[</span><span style="color:#abe338">&quot;user_id&quot;</span><span>]
</span></span><span>
</span><span><span>    </span><span style="color:#dcc6e0">for</span><span> i, msg </span><span style="color:#dcc6e0">in</span><span> </span><span style="color:#f5ab35">enumerate</span><span>(inputs[</span><span style="color:#abe338">&quot;setup_messages&quot;</span><span>]):
</span></span><span>        test_graph.invoke(
</span><span><span>            {</span><span style="color:#abe338">&quot;messages&quot;</span><span>: [HumanMessage(content=msg)]},
</span></span><span><span>            config={</span><span style="color:#abe338">&quot;configurable&quot;</span><span>: {
</span></span><span><span>                </span><span style="color:#abe338">&quot;thread_id&quot;</span><span>: </span><span style="color:#abe338">f&quot;setup-</span><span class="hljs-subst" style="color:#abe338">{user_id}</span><span style="color:#abe338">-</span><span class="hljs-subst" style="color:#abe338">{i}</span><span style="color:#abe338">&quot;</span><span>,
</span></span><span><span>                </span><span style="color:#abe338">&quot;user_id&quot;</span><span>: user_id,
</span></span><span>            }},
</span><span>        )
</span><span>
</span><span>    result = test_graph.invoke(
</span><span><span>        {</span><span style="color:#abe338">&quot;messages&quot;</span><span>: [HumanMessage(content=inputs[</span><span style="color:#abe338">&quot;test_question&quot;</span><span>])]},
</span></span><span><span>        config={</span><span style="color:#abe338">&quot;configurable&quot;</span><span>: {
</span></span><span><span>            </span><span style="color:#abe338">&quot;thread_id&quot;</span><span>: </span><span style="color:#abe338">f&quot;test-</span><span class="hljs-subst" style="color:#abe338">{user_id}</span><span style="color:#abe338">&quot;</span><span>,
</span></span><span><span>            </span><span style="color:#abe338">&quot;user_id&quot;</span><span>: user_id,
</span></span><span>        }},
</span><span>    )
</span><span>
</span><span><span>    </span><span style="color:#dcc6e0">return</span><span> {</span><span style="color:#abe338">&quot;response&quot;</span><span>: result[</span><span style="color:#abe338">&quot;messages&quot;</span><span>][-</span><span style="color:#f5ab35">1</span><span>].content}
</span></span><span>
</span><span>
</span><span>results = evaluate(
</span><span>    target,
</span><span><span>    data=</span><span style="color:#abe338">&quot;memory-persistence-evals&quot;</span><span>,
</span></span><span>    evaluators=[memory_judge, memory_recall],
</span><span><span>    experiment_prefix=</span><span style="color:#abe338">&quot;memory-persistence-v1&quot;</span><span>,
</span></span><span><span>    max_concurrency=</span><span style="color:#f5ab35">2</span><span>,
</span></span><span>)</span></code></pre><p>‍</p><p>The <code>memory_recall</code> evaluator is the one that catches the most regressions. If you change the extraction prompt and recall drops from 0.9 to 0.6, you know immediately. Without it, you find out from customer complaints three weeks later.</p><h2>When to Use This</h2><p><strong>Use checkpointer + Store when:</strong></p><ul role="list"><li>Customers interact across multiple sessions and expect continuity</li><li>Your agent asks repetitive setup questions that waste customer time</li><li>You need to personalize responses based on user history</li><li>Compliance requires maintaining an audit trail of what the agent &quot;knows&quot;</li></ul><p><strong>Use checkpointer only when:</strong></p><ul role="list"><li>All interactions are single-session (no returning customers)</li><li>Privacy requirements prohibit storing user data across sessions</li><li>Your use case is stateless Q&amp;A (FAQ bot, code assistant)</li></ul><p><strong>Skip both when:</strong></p><ul role="list"><li>Every request is independent (API endpoint, batch processing)</li><li>You&#x27;re already managing state externally (e.g., a CRM integration that passes context)<br/>‍</li></ul><div class="w-embed"><h2>More in This Series</h2>

<div style="margin-bottom:18px;">
  <a href="https://focused.io/lab/streaming-agent-state-with-langgraph" style="font-weight:600; text-decoration:none;">
    Streaming Agent State with LangGraph
  </a>
  <div style="font-size:15px; line-height:1.5; opacity:0.85;">
    Streaming node updates, token output, and custom events so users can see agent workflows as they execute.
  </div>
</div>

<div style="margin-bottom:18px;">
  <a href="https://focused.io/lab/your-ai-just-emailed-a-customer-without-permission" style="font-weight:600; text-decoration:none;">
    Your AI Just Emailed a Customer Without Permission
  </a>
  <div style="font-size:15px; line-height:1.5; opacity:0.85;">
    Human-in-the-loop approval patterns for controlling tool execution and preventing unsafe side effects.
  </div>
</div>

<div>
  <a href="https://focused.io/lab/your-customer-service-bot-is-slow-because-its-single-threaded" style="font-weight:600; text-decoration:none;">
    Your Customer Service Bot Is Slow Because It’s Single-Threaded
  </a>
  <div style="font-size:15px; line-height:1.5; opacity:0.85;">
    Parallel execution patterns for LangGraph agents that retrieve data, call tools, and synthesize results concurrently.
  </div>
</div></div><h2><br/>The Bottom Line</h2><p>LangGraph memory is two separate mechanisms and they should be treated that way. The checkpointer is infrastructure. Enable it so the graph can persist state within a thread and move on. The Store is different. It’s an application design problem where you need to decide what information is worth persisting, how it should be scoped, and when it should be removed.</p><p>For development, start with <code>InMemorySaver</code> and <code>InMemoryStore</code>. They’re simple and make it easy to validate memory behavior before introducing external persistence layers. Before expanding extraction logic, write a memory recall evaluation. If the agent cannot reliably retrieve stored facts, adding more extraction prompts will only increase noise in the system.</p><p>Use deterministic keys for attributes that change over time such as plan type or contact preferences, and use UUIDs for records that accumulate such as past issues or interaction summaries. Finally, add deduplication on the write path. Without it, memory stores grow quickly and retrieval quality degrades over time. This is a common failure mode in long-running agent systems.</p></div></div></div><div data-wf--spacer--variant="56px" class="spacer w-variant-452e6ede-4c8c-3880-d046-e036bae187d0"></div></div></div><div data-wf--spacer--variant="56px" class="spacer w-variant-452e6ede-4c8c-3880-d046-e036bae187d0"></div></div></div></header><section data-wf--section--background="base" class="section"><div class="anchor"></div><div class="padding-global"><div class="container-large"><div data-wf--spacer--variant="112px" class="spacer"></div><div><div data-cols="1fr 1fr" data-wf--header---two-columns--variant="reversed-light-purple-bg-shadow-2" class="header-two-columns w-variant-bd0ffe2b-9566-397a-6450-bcdbd2743df2"><div id="w-node-_983e24df-b330-b471-9a2d-f1c5df90d860-df90d85f" class="header-two-column-col"><div class="slot"><div data-wf--hubspot-form--variant="no-shadow-no-background" class="contact-form-wrapper w-variant-188aea06-9913-2e80-be73-25cde7cff85d"><div class="contact-form w-variant-188aea06-9913-2e80-be73-25cde7cff85d"><div data-formid="86a4ac18-eb5a-4c2a-b7a2-f864523e4173" class="w-embed w-script"><script>
(function () {
  const wrappers = Array.from(document.querySelectorAll(".contact-form"));
  if (!wrappers.length) return;

  let hubspotPromise = null;

  function loadHubspot() {
    if (window.hbspt?.forms) return Promise.resolve();
    if (hubspotPromise) return hubspotPromise;

    hubspotPromise = new Promise((resolve, reject) => {
      const existing = document.querySelector('script[src="https://js.hsforms.net/forms/embed/v2.js"]');

      if (existing) {
        existing.addEventListener("load", resolve, { once: true });
        existing.addEventListener("error", reject, { once: true });
        return;
      }

      const script = document.createElement("script");
      script.src = "https://js.hsforms.net/forms/embed/v2.js";
      script.async = true;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });

    return hubspotPromise;
  }

  function initWrapper(wrapper) {
    if (wrapper.dataset.hsInitialized === "true") return;
    wrapper.dataset.hsInitialized = "true";

    const formId = wrapper.querySelector("[data-formid]")?.getAttribute("data-formid");
    if (!formId) return;

    const success = wrapper.querySelector(".cstm-success-message");
    let mount = wrapper.querySelector(".hs-mount");

    if (!mount) {
      mount = document.createElement("div");
      mount.className = "hs-mount";
      wrapper.insertBefore(mount, success || null);
    }

    if (!mount.id) {
      mount.id = "hs_" + Math.random().toString(36).slice(2, 10);
    }

    loadHubspot().then(() => {
      window.hbspt.forms.create({
        region: "na1",
        portalId: "5845897",
        formId,
        target: "#" + mount.id,
        onFormSubmitted: () => {
          mount.style.display = "none";
          if (success) success.style.display = "block";
        }
      });
    });
  }

  function warmup() {
    loadHubspot().catch(() => {});
    window.removeEventListener("scroll", warmup);
    window.removeEventListener("mousemove", warmup);
    window.removeEventListener("touchstart", warmup);
    window.removeEventListener("focusin", warmup);
  }

  window.addEventListener("scroll", warmup, { once: true, passive: true });
  window.addEventListener("mousemove", warmup, { once: true, passive: true });
  window.addEventListener("touchstart", warmup, { once: true, passive: true });
  window.addEventListener("focusin", warmup, { once: true, passive: true });

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        initWrapper(entry.target);
      });
    }, {
      rootMargin: "1000px 0px"
    });

    wrappers.forEach((wrapper) => observer.observe(wrapper));
  } else {
    wrappers.forEach(initWrapper);
  }
})();
</script></div><div class="cstm-success-message"><p data-wf--paragraph--variant="paragraph-54px" class="paragraph w-variant-0f07cdc7-4852-e0fa-a59c-ffcd97e2e0d9 text-weight-bold">Your message has been sent!</p><p data-wf--paragraph--variant="paragraph-24px" class="paragraph w-variant-e29c16ba-6bd1-7c97-707a-26916cc18761 font-weight-bold">We’ll be in touch soon. In the mean time check out our case studies. </p><a data-wf--button--variant="base" href="/contact" class="button navbutton w-inline-block"><div>See all projects</div><div class="icon-embed-xxsmall w-embed"><svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 16 16" fill="none" preserveAspectRatio="xMidYMid meet" aria-hidden="true" role="img">
<g clip-path="url(#clip0_38_3)">
<path d="M9.59961 1.70007L14.9996 8.00007L9.59961 14.3001" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
<path d="M0.898438 8.00006H14.9991" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
</g>
<defs>
<clipPath id="clip0_38_3">
<rect width="16" height="16" fill="white"/>
</clipPath>
</defs>
</svg></div></a></div></div></div></div></div><div id="w-node-_983e24df-b330-b471-9a2d-f1c5df90d868-df90d85f" class="header-two-column-col w-variant-bd0ffe2b-9566-397a-6450-bcdbd2743df2"><div class="h-100"><div data-wf--content-wrapper--variant="base" class="content-wrapper"><div data-wf--spacer--variant="0px" class="spacer w-variant-301f2f49-ba85-8507-11a1-c51f9e40b381"></div><div class="content"><span data-wf--label--variant="base" class="heading-label">/Contact Us</span><h2 data-wf--heading--variant="heading-style-h2" class="heading-style w-variant-eb7094f4-0e88-b38d-4a44-09af707e4a20">Let&#x27;s Build better Agents Together</h2></div><div data-wf--spacer--variant="0px" class="spacer w-variant-301f2f49-ba85-8507-11a1-c51f9e40b381"></div></div><div class="lottie-animation-wrapper" data-speed="0.6" data-h="" data-left="-25%" data-bottom="-12%" data-pos="absolute" data-top="" data-w="128%" data-right=""><div data-lottie="https://cdn.prod.website-files.com/6915b44a5861a2536d561406/69429115fe70565086f7c83d_contact_form.json" class="lottie-box"></div></div></div></div><div class="header-two-columns-image-wrapper"><img src="https://cdn.prod.website-files.com/6915b44a5861a2536d561406/692048c2d4229a8bdd5a7683_Focused_JT_Bio.webp" loading="lazy" alt="" sizes="100vw" srcset="https://cdn.prod.website-files.com/6915b44a5861a2536d561406/692048c2d4229a8bdd5a7683_Focused_JT_Bio-p-500.webp 500w, https://cdn.prod.website-files.com/6915b44a5861a2536d561406/692048c2d4229a8bdd5a7683_Focused_JT_Bio.webp 534w" class="header-two-columns-image"/></div><div class="header-two-columns-image-cover"></div></div></div><div data-wf--spacer--variant="112px" class="spacer"></div></div></div></section><div class="small-cta_component"><div class="padding-global"><div class="container-large"><div class="small-cta-content"><h2 data-wf--heading--variant="heading-style-h4" class="heading-style w-variant-a0e6fd3e-b805-f682-c714-5c6a16376d25">Modernize your legacy with Focused</h2><a data-wf--button--variant="base" href="/contact" class="button navbutton w-inline-block"><div>Get in touch</div><div class="icon-embed-xxsmall w-embed"><svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 16 16" fill="none" preserveAspectRatio="xMidYMid meet" aria-hidden="true" role="img">
<g clip-path="url(#clip0_38_3)">
<path d="M9.59961 1.70007L14.9996 8.00007L9.59961 14.3001" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
<path d="M0.898438 8.00006H14.9991" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
</g>
<defs>
<clipPath id="clip0_38_3">
<rect width="16" height="16" fill="white"/>
</clipPath>
</defs>
</svg></div></a></div></div></div></div><footer class="footer"><div class="padding-global"><div class="container-large"><div class="footer-grid"><div id="w-node-_4d686aeb-fbb6-3585-52b1-1e05afe41394-afe41390" class="footer-grid--item"><a aria-label="Focused" href="/" class="w-inline-block"><img src="https://cdn.prod.website-files.com/6915b44a5861a2536d561406/6926f90025623396d545b2bc_footer-logo.svg" loading="lazy" alt="Focused"/></a></div><div id="w-node-_4d686aeb-fbb6-3585-52b1-1e05afe41397-afe41390" class="footer-grid--item is-address"><div class="footer_rich-text w-richtext"><p>433 W Van Buren St</p><p>Suite 1100-C <br/>Chicago, IL 60607</p><p>‍<br/>‍<a href="#">work@focused.io<br/>‍</a><a href="mailto:+7083038088">(708) 303-8088</a></p></div></div><div id="w-node-_4d686aeb-fbb6-3585-52b1-1e05afe413a5-afe41390" class="footer-grid--item links-grid"><nav class="footer-links-grid"><div class="footer-links-item"><a href="/about" class="footer-link">About</a></div><div class="footer-links-item"><a href="/about#leadership" class="footer-link"><strong>Leadership</strong></a></div><div class="footer-links-item"><a href="/capabilities" class="footer-link"><strong>Capabilities</strong></a></div><div class="footer-links-item"><a href="/case-studies" class="footer-link"><strong>Case Studies</strong></a></div><div class="footer-links-item"><a href="/lab" class="footer-link"><strong>Focused Lab</strong></a></div><div class="footer-links-item"><a href="/careers" class="footer-link"><strong>Careers</strong></a></div><div class="footer-links-item"><a href="/contact" class="footer-link"><strong>Contact</strong></a></div><div class="footer-links-item"><a href="/lab/rss.xml" class="footer-link"><strong>RSS</strong></a></div></nav></div><div id="w-node-_4d686aeb-fbb6-3585-52b1-1e05afe413c2-afe41390" class="footer-grid--item ml-auto"><div class="footer--achievements"><div class="footer--achievements-item"><img src="https://cdn.prod.website-files.com/6915b44a5861a2536d561406/6926fae26f61ef6bca7276b5_footer-inc-5000.webp" loading="lazy" alt="" class="footer--achievements-item-img"/></div><div class="footer--achievements-item"><img src="https://cdn.prod.website-files.com/6915b44a5861a2536d561406/6926fae26f61ef6bca7276ac_footer-bptw.webp" loading="lazy" alt="" class="footer--achievements-item-img"/></div></div></div><div id="w-node-_4d686aeb-fbb6-3585-52b1-1e05afe413c8-afe41390" class="footer-grid--item footer--copyright"><div>© 2026 Focused. All rights reserved.</div><div><a href="/privacy-policy" class="footnote-link">Privacy Policy</a></div></div><div id="w-node-_4d686aeb-fbb6-3585-52b1-1e05afe413ce-afe41390" class="footer-grid--item footer--social"><a aria-label="Facebook" href="https://www.facebook.com/withfocus" target="_blank" class="social-icon-button w-inline-block"><div class="social-icon-button-icon w-embed"><svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 32 32" fill="none" preserveAspectRatio="xMidYMid meet" aria-hidden="true" role="img">
									<path fill-rule="evenodd" clip-rule="evenodd" d="M17.1302 25.5701V16.8224H20.193L20.6515 13.4132H17.1302V11.2366C17.1302 10.2495 17.4161 9.5769 18.8925 9.5769L20.7755 9.57606V6.5269C20.4498 6.48543 19.3321 6.39258 18.0317 6.39258C15.3168 6.39258 13.4582 7.98131 13.4582 10.899V13.4132H10.3877V16.8224H13.4582V25.5701H17.1302Z" fill="currentColor"/>
								</svg></div></a><a aria-label="Linkedin" href="https://www.linkedin.com/company/focused-dot-io" target="_blank" class="social-icon-button w-inline-block"><div class="social-icon-button-icon w-embed"><svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 33 32" fill="none" preserveAspectRatio="xMidYMid meet" aria-hidden="true" role="img">
									<g clip-path="url(#clip0_8001_1572)">
										<path d="M11.8699 12.874H8.82202C8.68675 12.874 8.57715 12.9837 8.57715 13.1189V22.9104C8.57715 23.0456 8.68675 23.1552 8.82202 23.1552H11.8699C12.0052 23.1552 12.1148 23.0456 12.1148 22.9104V13.1189C12.1148 12.9837 12.0052 12.874 11.8699 12.874Z" fill="currentColor"/>
										<path d="M10.3471 8.00684C9.23815 8.00684 8.33594 8.90807 8.33594 10.0158C8.33594 11.1241 9.23815 12.0257 10.3471 12.0257C11.4553 12.0257 12.3567 11.124 12.3567 10.0158C12.3568 8.90807 11.4553 8.00684 10.3471 8.00684Z" fill="currentColor"/>
										<path d="M19.6217 12.6309C18.3975 12.6309 17.4926 13.1571 16.9438 13.755V13.1191C16.9438 12.9839 16.8342 12.8742 16.6989 12.8742H13.78C13.6448 12.8742 13.5352 12.9839 13.5352 13.1191V22.9106C13.5352 23.0458 13.6448 23.1554 13.78 23.1554H16.8212C16.9565 23.1554 17.0661 23.0458 17.0661 22.9106V18.0661C17.0661 16.4336 17.5095 15.7976 18.6475 15.7976C19.8869 15.7976 19.9854 16.8171 19.9854 18.15V22.9106C19.9854 23.0459 20.095 23.1555 20.2302 23.1555H23.2726C23.4078 23.1555 23.5174 23.0459 23.5174 22.9106V17.5398C23.5174 15.1124 23.0546 12.6309 19.6217 12.6309Z" fill="currentColor"/>
									</g>
									<defs>
										<clipPath id="clip0_8001_1572">
											<rect width="15.1822" height="15.1822" fill="currentColor" transform="translate(8.33594 7.99023)"/>
										</clipPath>
									</defs>
								</svg></div></a><a aria-label="X" href="https://x.com/focused_dot_io" target="_blank" class="social-icon-button w-inline-block"><div class="social-icon-button-icon w-embed"><svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 33 32" fill="none" preserveAspectRatio="xMidYMid meet" aria-hidden="true" role="img">
									<path d="M21.2678 8.79004H23.7183L18.3647 14.8827L24.6629 23.1732H19.7313L15.8689 18.1449L11.4493 23.1732H8.99718L14.7234 16.6565L8.68164 8.79004H13.7382L17.2296 13.386L21.2678 8.79004ZM20.4077 21.7127H21.7657L13.0004 10.1739H11.5434L20.4077 21.7127Z" fill="currentColor"/>
								</svg></div></a><a aria-label="Github" href="https://github.com/focused-dot-io" target="_blank" class="social-icon-button w-inline-block"><div class="social-icon-button-icon w-embed"><svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 32 32" fill="none" preserveAspectRatio="xMidYMid meet" aria-hidden="true" role="img">
									<path fill-rule="evenodd" clip-rule="evenodd" d="M15.8784 5.59375C10.032 5.59375 5.30566 10.3549 5.30566 16.2451C5.30566 20.9534 8.33397 24.939 12.535 26.3496C13.0603 26.4556 13.2527 26.1204 13.2527 25.8384C13.2527 25.5914 13.2354 24.745 13.2354 23.8632C10.2943 24.4981 9.68181 22.5934 9.68181 22.5934C9.20916 21.359 8.50884 21.0417 8.50884 21.0417C7.54622 20.3892 8.57896 20.3892 8.57896 20.3892C9.64675 20.4598 10.2071 21.4826 10.2071 21.4826C11.1521 23.1048 12.6751 22.6465 13.2877 22.3643C13.3752 21.6765 13.6554 21.2004 13.953 20.9359C11.6073 20.689 9.13926 19.772 9.13926 15.6807C9.13926 14.5168 9.5591 13.5646 10.2244 12.824C10.1194 12.5595 9.75171 11.466 10.3295 10.0024C10.3295 10.0024 11.2223 9.72015 13.2351 11.0957C14.0969 10.8625 14.9857 10.7439 15.8784 10.7429C16.7712 10.7429 17.6812 10.8665 18.5215 11.0957C20.5346 9.72015 21.4274 10.0024 21.4274 10.0024C22.0052 11.466 21.6373 12.5595 21.5323 12.824C22.2151 13.5646 22.6176 14.5168 22.6176 15.6807C22.6176 19.772 20.1496 20.6712 17.7864 20.9359C18.1716 21.2709 18.504 21.9057 18.504 22.9109C18.504 24.3393 18.4867 25.4856 18.4867 25.8382C18.4867 26.1204 18.6793 26.4556 19.2043 26.3498C23.4054 24.9387 26.4337 20.9534 26.4337 16.2451C26.451 10.3549 21.7074 5.59375 15.8784 5.59375Z" fill="currentColor"/>
								</svg></div></a></div></div></div></div><div class="footer-gradient-spacer"></div></footer></div></div><script src="https://d3e54v103j8qbb.cloudfront.net/js/jquery-3.5.1.min.dc5e7f18c8.js?site=6915b44a5861a2536d561406" type="text/javascript" integrity="sha256-9/aliU8dGd2tb6OSsuzixeV4y/faTqgFtohetphbbj0=" crossorigin="anonymous"></script><script src="https://cdn.prod.website-files.com/6915b44a5861a2536d561406/js/webflow.0d178927.bf64905a7f6f125c.js" type="text/javascript" integrity="sha384-TUCfEjuWJ/c5sWRMBJadRqOy9sqDAwvBwVKLRgLeRsAqNsbDTNylL5fO06fQjorE" crossorigin="anonymous"></script><script>
  document.addEventListener('DOMContentLoaded', function () {
    const swiperEl = document.querySelector('.feature_card-swiper');
    if (!swiperEl) return;

    function storeOriginalIframeSrcs() {
      swiperEl.querySelectorAll('.swiper-slide iframe').forEach(function (iframe) {
        const src = iframe.getAttribute('src') || iframe.src;
        if (src && src !== 'about:blank' && !iframe.dataset.originalSrc) {
          iframe.dataset.originalSrc = src;
        }
      });
    }

    function stopInactiveVideos(activeSlideEl) {
      if (!activeSlideEl) return;

      swiperEl.querySelectorAll('.swiper-slide').forEach(function (slide) {
        const iframe = slide.querySelector('iframe');
        if (!iframe) return;

        const originalSrc = iframe.dataset.originalSrc;
        if (!originalSrc) return;

        if (slide === activeSlideEl) {
          if (iframe.src !== originalSrc) {
            iframe.src = originalSrc;
          }
        } else {
          if (iframe.src && iframe.src !== 'about:blank') {
            iframe.src = 'about:blank';
          }
        }
      });
    }

    const swiper = new Swiper('.feature_card-swiper', {
      slidesPerView: 1,
      loop: true,
      a11y: {
        enabled: false,
      },
      spaceBetween: 0,
      navigation: {
        nextEl: '.icon-embed.is-next',
        prevEl: '.icon-embed.is-prev',
      },
      on: {
        init: function () {
          storeOriginalIframeSrcs();

          setTimeout(function () {
            storeOriginalIframeSrcs();
            stopInactiveVideos(swiperEl.querySelector('.swiper-slide-active'));
          }, 300);

          updateCounter(this);
          stopInactiveVideos(swiperEl.querySelector('.swiper-slide-active'));
        },
        slideChange: function () {
          updateCounter(this);
        },
        slideChangeTransitionEnd: function (swiper) {
          const activeSlide = swiper.slides[swiper.activeIndex];
          stopInactiveVideos(activeSlide);
        },
      },
    });

    function updateCounter(swiper) {
      const current = swiper.realIndex + 1;
      const total = swiperEl.querySelectorAll('.swiper-slide:not(.swiper-slide-duplicate)').length;

      const activeEl = document.querySelector('.active-slide');
      const totalEl = document.querySelector('.number-of-slides');

      if (activeEl) activeEl.textContent = String(current).padStart(2, '0');
      if (totalEl) totalEl.textContent = String(total).padStart(2, '0');
    }
  });
</script>

<script src="https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js"></script>
  <script>
    (function () {
      function initLottieEmbeds() {
        document.querySelectorAll(".lottie-animation-wrapper").forEach(function (wrapper) {
          ["w", "h", "pos", "top", "bottom", "left", "right"].forEach(function (a) {
            var val = wrapper.getAttribute("data-" + a);
            if (val !== null) wrapper.style.setProperty("--" + a, val);
          });
        });

        document.querySelectorAll(".lottie-box").forEach(function (box) {
          if (box.dataset.lottieLoaded === "true") return;
          box.dataset.lottieLoaded = "true";

          var src = box.getAttribute("data-lottie");
          if (!src) return;

          var fullUrl = new URL(src, window.location.href).href;
          var assetsPath = fullUrl.replace(/[^/]+$/, "");

          var wrapper = box.closest(".lottie-animation-wrapper");
          var speedAttr = wrapper ? wrapper.getAttribute("data-speed") : null;
          var speed = parseFloat(speedAttr);
          if (!isFinite(speed) || speed <= 0) speed = 1;

          var renderer = box.getAttribute("data-renderer") || "svg";

          var anim = lottie.loadAnimation({
            container: box,
            renderer: renderer,
            loop: true,
            autoplay: true,
            path: fullUrl,
            assetsPath: assetsPath,
            rendererSettings: {
              preserveAspectRatio: "xMidYMid meet",
              progressiveLoad: true
            }
          });

          anim.setSpeed(speed);

          anim.addEventListener("DOMLoaded", function () {
            if (typeof anim.resize === "function") anim.resize();
          });
        });
      }

      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initLottieEmbeds);
      } else {
        initLottieEmbeds();
      }

      var resizeTimer;
      window.addEventListener("resize", function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () {
          document.querySelectorAll(".lottie-box svg").forEach(function (svg) {
            svg.style.width = "";
            svg.style.height = "";
          });
        }, 100);
      }, { passive: true });
    })();
  </script><script src="https://hubspotv2.use1-marketplace-1p-apps-prod-red.if.webflow.services/static/loader.js" type="text/javascript" async="" defer=""></script><script src="https://hubspotv2.use1-marketplace-1p-apps-prod-red.if.webflow.services/static/disable-hubspot-chatbot.js" type="text/javascript" async="" defer=""></script></body></html>