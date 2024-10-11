import { Box, Button, IconButton } from '@mui/material';
import { Delete } from '@mui/icons-material';
import * as React from 'react';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';

const StyledBox = styled(Box)`
  width: 100%;
  height: 30px;
  background-color: #f4f5f6;
  color: '#404040';
`;

interface IdDivProps {
  isDeleted: boolean;
}

const IdDiv = styled.div<IdDivProps>`
  text-decoration: ${({ isDeleted }) => (isDeleted ? 'line-through' : 'none')};
`;
interface ExcludedItemProps {
  id: string;
  onDelete;
  onUndo;
  isDeleted: boolean;
  isEdit: boolean;
}

export function ExcludedItem({
  id,
  onDelete,
  onUndo,
  isDeleted,
  isEdit,
}: ExcludedItemProps): React.ReactElement {
  const { t } = useTranslation();

  return (
    <StyledBox
      display="flex"
      alignItems="center"
      justifyContent="space-between"
      pl={8}
      pr={8}
      pt={4}
      pb={4}
      mt={2}
    >
      <IdDiv isDeleted={isDeleted}>{id}</IdDiv>
      {isEdit &&
        (isDeleted ? (
          <Button variant="text" color="primary" onClick={onUndo}>
            {t('Undo')}
          </Button>
        ) : (
          <IconButton onClick={onDelete}>
            <Delete />
          </IconButton>
        ))}
    </StyledBox>
  );
}
