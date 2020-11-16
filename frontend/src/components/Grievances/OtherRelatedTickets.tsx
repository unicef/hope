import { Box, Typography } from '@material-ui/core';
import React from 'react';
import styled from 'styled-components';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import { ContentLink } from '../ContentLink';
import { LabelizedField } from '../LabelizedField';

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

export const OtherRelatedTickets = () => {
  const businessArea = useBusinessArea();

  const ids = ['HH-22222', 'HH-33333'];
  const mappedIds = ids.map((id) => (
    <ContentLink href={`/${businessArea}/payment-records/${id}`}>
      {id}
    </ContentLink>
  ));

  return (
    <StyledBox>
      <Title>
        <Typography variant='h6'>Other Related Tickets</Typography>
      </Title>
      <Box display='flex' flexDirection='column'>
        <LabelizedField label='For Household'>
          <>{mappedIds}</>
        </LabelizedField>
      </Box>
    </StyledBox>
  );
};
