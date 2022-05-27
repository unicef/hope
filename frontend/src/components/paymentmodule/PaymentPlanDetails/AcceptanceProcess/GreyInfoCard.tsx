import { Box } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';

const GreyText = styled.div`
  color: #9e9e9e;
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
    <GreyBox p={3}>
      Approved by someone<GreyText>on 01/01/2022</GreyText>
    </GreyBox>
  );
}
