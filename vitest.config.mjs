import { defineConfig } from 'vitest/config';

process.env.TZ = 'America/Los_Angeles';

export default defineConfig({
  test: {
    environment: 'jsdom',
    include: ['tests/frontend/**/*.test.js'],
  },
});
