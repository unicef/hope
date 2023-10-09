import { Box, Button, Typography } from '@material-ui/core';
import ExpandLessIcon from '@material-ui/icons/ExpandLess';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { Title } from '../../../core/Title';
import { AcceptanceProcessRow } from './AcceptanceProcessRow';

const ButtonContainer = styled(Box)`
  width: 200px;
`;

interface AcceptanceProcessProps {
  records;
}

export const AcceptanceProcess = ({
  records,
}: AcceptanceProcessProps): React.ReactElement => {
  const { t } = useTranslation();
  const [showAll, setShowAll] = useState(false);

  const renderRows = (): React.ReactElement => {
    if (showAll) {
      return records.map(({ node }) => (
        <AcceptanceProcessRow
          key={node.id}
          acceptanceProcess={node}
          showDivider
        />
      ));
    }
    return <AcceptanceProcessRow acceptanceProcess={records[0].node} />;
  };

  const renderShowMore = (): React.ReactElement | boolean => {
    if (records.length <= 1) {
      return false;
    }

    if (showAll) {
      return (
        <ButtonContainer>
          <Button
            variant='outlined'
            color='primary'
            onClick={() => setShowAll(!showAll)}
            endIcon={<ExpandLessIcon />}
            data-cy='btn-hide'
          >
            {t('HIDE')}
          </Button>
        </ButtonContainer>
      );
    }

    return (
      <ButtonContainer>
        <Button
          variant='outlined'
          color='primary'
          onClick={() => setShowAll(!showAll)}
          endIcon={<ExpandMoreIcon />}
          data-cy='btn-show-previous'
        >
          {t('SHOW PREVIOUS')}
        </Button>
      </ButtonContainer>
    );
  };

  if (!records.length) {
    return null;
  }

  return (
    <Box m={5}>
      <Box display='flex' justifyContent='space-between' mt={4}>
        <Title>
          <Typography variant='h6' data-cy='title-acceptance-process'>
            {t('Acceptance Process')}
          </Typography>
        </Title>
      </Box>
      {renderRows()}
      {renderShowMore()}
    </Box>
  );
};
