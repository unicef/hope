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
// The backend parser only accepts this sheet (XlsxPaymentPlanBaseService.TITLE), so the
// preview must count the same one — not whatever happens to be first in the workbook.
const SHEET_NAME = 'Payment Plan - Payment List';

export async function countTopUpAmountRows(file: File): Promise<number | null> {
  let headers: unknown[] | undefined;
  let dataRows: unknown[][];
  try {
    [headers, ...dataRows] = await readSheet(file, SHEET_NAME);
  } catch {
    return null;
  }

  const amountColumn = headers?.indexOf(AMOUNT_HEADER) ?? -1;
  if (amountColumn === -1) return null;

  // Counts only cells Excel stored as a positive number, which is not what the server does:
  // it rejects the whole file over a negative or non-numeric cell that is skipped here, and
  // funds a number stored as text that this misses. A preview, not a validation.
  return dataRows.filter((row) => {
    const amount = row[amountColumn];
    return typeof amount === 'number' && amount > 0;
  }).length;
}
