import { MouseEventHandler, ReactElement, useState } from 'react';
import TableRow, { TableRowProps } from '@mui/material/TableRow';
import styled from 'styled-components';

const StyledTableRow = styled(TableRow)`
  cursor: pointer;
  && {
    white-space: nowrap;
    overflow: auto;
  }
`;
// Legacy IE-only `document.selection` API, absent from the standard DOM lib.
type LegacyDocument = Document & {
  selection?: { type: string; createRange: () => { text: string } };
};

function getSelectedText(): string {
  let text = '';
  if (window.getSelection !== undefined) {
    text = window.getSelection().toString();
  } else {
    const legacyDocument = document as LegacyDocument;
    if (
      legacyDocument.selection !== undefined &&
      legacyDocument.selection.type === 'Text'
    ) {
      text = legacyDocument.selection.createRange().text;
    }
  }
  return text;
}

export function ClickableTableRow({
  onClick,
  ...props
}: TableRowProps): ReactElement {
  const [selectedText, setSelectedText] = useState('');
  let realOnClick: MouseEventHandler<HTMLTableRowElement>;
  let onMouseDown: MouseEventHandler<HTMLTableRowElement>;
  if (onClick) {
    onMouseDown = () => {
      setSelectedText(getSelectedText());
    };
    realOnClick = (event) => {
      const altPressed = event.getModifierState('Alt');
      if (altPressed) {
        return;
      }
      if (selectedText.length === 0 && getSelectedText().length > 0) {
        return;
      }
      onClick(event);
    };
  }
  return (
    <StyledTableRow
      {...props}
      onMouseDown={onMouseDown}
      onClick={realOnClick}
    />
  );
}
