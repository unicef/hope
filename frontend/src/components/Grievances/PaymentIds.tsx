import { Box, Typography } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { ContentLink } from '../ContentLink';

const StyledBox = styled.div`
  border-color: #b1b1b5;
  border-bottom-width: 1px;
  border-bottom-style: solid;
  border-radius: 3px;
  background-color: #fff;
  display: flex;
  flex-direction: column;
  width: 100%;
  padding: 26px 22px;
`;
const Title = styled.div`
  padding-bottom: ${({ theme }) => theme.spacing(8)}px;
`;

export const PaymentIds = ({ ids }: { ids: string[] }) => {
  const businessArea = useBusinessArea();

  const mappedIds = ids.map((id) => (
    <Box mb={1}>
      <ContentLink href={`/${businessArea}/payment-records/${id}`}>
        {id}
      </ContentLink>
    </Box>
  ));
  return (
    <StyledBox>
      <Title>
        <Typography variant='h6'>Payment Ids</Typography>
      </Title>
      <Box display='flex' flexDirection='column'>
        {mappedIds}
      </Box>
    </StyledBox>
  );
};
