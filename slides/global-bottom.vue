<template>
  <footer class="absolute bottom-0 left-0 right-0 w-full z-50 bg-light-background dark:bg-dark-background">
    <div class="flex w-full px-14 pt-10 pb-4 justify-between items-end">
      <span class="text-xs tracking-wide opacity-30">pdf-document-layout-analysis</span>
      <span class="text-xs tracking-wide opacity-30">HURIDOCS</span>
    </div>
  </footer>
</template>

<style>
/* The theme renders its own footer first; ours sits last. Keep only ours. */
footer:not(:last-of-type) {
  display: none !important;
}
</style>
