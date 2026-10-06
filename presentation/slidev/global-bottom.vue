<template>
  <footer class="deck-footer">
    <span>JEV / {{ $nav.currentPage > 15 ? 'APPENDIX' : 'DECISION MODELS FOR AGENTS' }}</span>
    <span class="page-number">{{ $nav.currentPage }} / {{ $nav.total }}</span>
  </footer>
</template>
