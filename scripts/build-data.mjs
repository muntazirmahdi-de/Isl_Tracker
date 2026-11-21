// Runs in GitHub Actions: scrape once, write a static JSON file the page reads.
import { mkdir, writeFile } from "node:fs/promises";
import { fetchApplicants } from "../lib/fetchApplicants.js";

const records = await fetchApplicants({ forceRefresh: true });
if (!records.length) throw new Error("Scrape returned 0 records — not publishing empty data.");

await mkdir("_site/data", { recursive: true });
await writeFile(
  "_site/data/applicants.json",
  JSON.stringify({ updatedAt: new Date().toISOString(), records })
);
console.log(`Wrote ${records.length} records`);
