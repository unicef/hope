import { Box } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { MessageDialog } from './MessageDialog';

const GreyText = styled.div`
  color: #9e9e9e;
`;

const GreyTitle = styled.div`
  color: #7c8990;
  text-transform: uppercase;
  font-size: 12px;
`;

const GreyBox = styled(Box)`
  background-color: #f4f5f6;
`;
interface GreyInfoCardProps {
  businessArea?: string;
  permissions?: string[];
}

export function GreyInfoCard({
  businessArea,
  permissions,
}: GreyInfoCardProps): React.ReactElement {
  const { t } = useTranslation();

  return (
    <Box display='flex' flexDirection='column'>
      <Box p={3}>
        <GreyTitle>Sent for approval by martin scott on 01/01/2022</GreyTitle>
      </Box>
      <GreyBox display='flex' alignItems='center' ml={3} mr={3} p={3}>
        Approved by someone
        <Box ml={1}>
          <GreyText>on 01/01/2022</GreyText>
        </Box>
        <MessageDialog
          message='I rejected it because I felt it was wrong.'
          author='Bob Ugar'
          date='12/02/2022'
        />
      </GreyBox>
    </Box>
  );
}
