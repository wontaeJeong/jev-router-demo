import Reveal from 'reveal.js';
import Markdown from 'reveal.js/plugin/markdown/markdown.esm.js';
import Highlight from 'reveal.js/plugin/highlight/highlight.esm.js';
import Notes from 'reveal.js/plugin/notes/notes.esm.js';
import 'reveal.js/dist/reveal.css';
import 'reveal.js/plugin/highlight/monokai.css';
import './theme.css';
import talk from '../../talk.md?raw';

const source = document.createElement('section');
source.setAttribute('data-markdown', '');
source.setAttribute('data-separator', '^---$');
source.setAttribute('data-separator-notes', '^Note:');
const template = document.createElement('textarea');
template.setAttribute('data-template', '');
template.textContent = talk;
source.append(template);
document.querySelector('.slides').append(source);

const deck = new Reveal({
  width: 1600,
  height: 900,
  margin: 0.04,
  minScale: 0.1,
  maxScale: 2,
  center: false,
  view: 'slide',
  hash: true,
  history: true,
  controls: true,
  controlsTutorial: false,
  progress: true,
  slideNumber: 'c/t',
  showSlideNumber: 'all',
  keyboard: true,
  transition: 'fade',
  transitionSpeed: 'fast',
  backgroundTransition: 'none',
  pdfSeparateFragments: false,
  pdfMaxPagesPerSlide: 1,
  plugins: [Markdown, Highlight, Notes],
});

// The bundled speaker view uses Reveal's postMessage API and public instance.
window.Reveal = deck;
deck.initialize();
