import { Box, IconButton } from '@material-ui/core';
import { Delete } from '@material-ui/icons';
import React from 'react';
import styled from 'styled-components';

const StyledBox = styled(Box)`
  width: 100%;
  height: 30px;
  background-color: #f4f5f6;
  color: '#404040';
`;

interface ExcludedItemProps {
  id: string;
  onDelete;
}

export const ExcludedItem = ({
  id,
  onDelete,
}: ExcludedItemProps): React.ReactElement => {
  return (
    <StyledBox
      display='flex'
      alignItems='center'
      justifyContent='space-between'
      pl={8}
      pr={8}
      pt={4}
      pb={4}
      mt={2}
    >
      {id}
      <IconButton onClick={onDelete}>
        <Delete />
      </IconButton>
    </StyledBox>
  );
};
