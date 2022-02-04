import React, { MouseEventHandler, useState } from 'react';
import TableRow, { TableRowProps } from '@material-ui/core/TableRow';
import styled from 'styled-components';

const StyledTableRow = styled(TableRow)`
  cursor: pointer;
`;
function getSelectedText(): string {
  let text = '';
  if (window.getSelection !== undefined) {
    text = window.getSelection().toString();
  } else if (
    // eslint-disable-next-line @typescript-eslint/ban-ts-ignore
    // @ts-ignore
    document.selection !== undefined &&
    // eslint-disable-next-line @typescript-eslint/ban-ts-ignore
    // @ts-ignore
    document.selection.type === 'Text'
  ) {
    // eslint-disable-next-line @typescript-eslint/ban-ts-ignore
    // @ts-ignore
    text = document.selection.createRange().text;
  }
  return text;
}

export function ClickableTableRow({
  onClick,
  ...props
}: TableRowProps): React.ReactElement {
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
