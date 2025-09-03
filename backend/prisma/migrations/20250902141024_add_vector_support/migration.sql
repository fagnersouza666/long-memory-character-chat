/*
  Warnings:

  - You are about to alter the column `embedding` on the `DocumentChunk` table. The data in that column could be lost. The data in that column will be cast from `ByteA` to `Unsupported("vector")`.

*/
-- AlterTable
ALTER TABLE "DocumentChunk" ALTER COLUMN "embedding" SET DATA TYPE vector;
