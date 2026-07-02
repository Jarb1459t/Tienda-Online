import { defineConfig } from 'prisma';

export default defineConfig({
  datasource: {
    // Esto le dice a Prisma que busque la variable DATABASE_URL en tu sistema
    url: process.env.DATABASE_URL,
  },
});