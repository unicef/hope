// The package has no root export; /browser is the build that takes a File straight from the input.
// readSheet returns the rows of one sheet — the default export returns every sheet wrapped.
import { readSheet } from 'read-excel-file/browser';

/**
 * Count the beneficiaries a filled-in Top-Up amount template would actually fund.
 *
 * Only a preview for the upload field — the backend re-parses the file and has the final say.
 * Returns null when the file is not a readable Top-Up template; the caller then shows nothing
 * and lets the server produce the real error on submit.
 */

const AMOUNT_HEADER = 'entitlement_quantity';

export async function countTopUpAmountRows(file: File): Promise<number | null> {
  let headers: unknown[] | undefined;
  let dataRows: unknown[][];
  try {
    [headers, ...dataRows] = await readSheet(file);
  } catch {
    return null;
  }

  const amountColumn = headers?.indexOf(AMOUNT_HEADER) ?? -1;
  if (amountColumn === -1) return null;

  // Blank, zero and non-numeric rows fund nobody — the same rule parse_top_up_amount_file
  // applies server-side.
  return dataRows.filter((row) => {
    const amount = row[amountColumn];
    return typeof amount === 'number' && amount > 0;
  }).length;
}
