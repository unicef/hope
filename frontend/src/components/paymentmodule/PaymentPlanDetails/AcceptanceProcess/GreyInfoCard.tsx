import { Box } from '@material-ui/core';
import React from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { UniversalMoment } from '../../../core/UniversalMoment';
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
  topMessage: string;
  topDate: string;
  bottomMessage: string;
  bottomDate: string;
  comment?: string;
  commentAuthor?: string;
  commentDate?: string;
}

export const GreyInfoCard = ({
  topMessage,
  topDate,
  bottomMessage,
  bottomDate,
  comment,
  commentAuthor,
  commentDate,
}: GreyInfoCardProps): React.ReactElement => {
  const { t } = useTranslation();

  return (
    <Box display='flex' flexDirection='column'>
      <Box p={3}>
        <GreyTitle>
          {topMessage} on <UniversalMoment>{topDate}</UniversalMoment>
        </GreyTitle>
      </Box>
      <GreyBox display='flex' alignItems='center' ml={3} mr={3} p={3}>
        {bottomMessage}
        <Box ml={1}>
          <GreyText>
            on <UniversalMoment>{bottomDate}</UniversalMoment>
          </GreyText>
        </Box>
        {comment && (
          <MessageDialog
            comment={comment}
            author={commentAuthor}
            date={commentDate}
          />
        )}
      </GreyBox>
    </Box>
  );
};
