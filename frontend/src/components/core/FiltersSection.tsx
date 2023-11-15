import { Box, Button, Collapse, Grid } from '@material-ui/core';
import Paper from '@material-ui/core/Paper';
import ExpandLess from '@material-ui/icons/ExpandLessRounded';
import ExpandMore from '@material-ui/icons/ExpandMoreRounded';
import React, { ReactElement, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import { ClearApplyButtons } from './ClearApplyButtons';

interface FiltersSectionProps {
  children: ReactElement | ReactElement[];
  clearHandler: () => void;
  applyHandler: () => void;
  isOnPaper?: boolean;
}

const FiltersPaper = styled(Paper)`
  width: 100%;
  background-color: #fff;
  padding: ${({ theme }) => theme.spacing(2)}px
    ${({ theme }) => theme.spacing(11)}px;
`;

export const FiltersSection: React.FC<FiltersSectionProps> = ({
  children,
  clearHandler,
  applyHandler,
  isOnPaper = true,
}): ReactElement => {
  const [expanded, setExpanded] = useState(true);
  const { t } = useTranslation();

  const filtersComponent = (
    <>
      <Grid container alignItems='flex-end' spacing={3}>
        <Box
          pt={4}
          pb={4}
          display='flex'
          alignItems='center'
          justifyContent='flex-start'
          width='100%'
        >
          <Button
            variant='text'
            color='primary'
            endIcon={expanded ? <ExpandLess /> : <ExpandMore />}
            onClick={() => setExpanded(!expanded)}
            data-cy='button-filters-expand'
          >
            {expanded ? t('HIDE FILTERS') : t('SHOW FILTERS')}
          </Button>
        </Box>
      </Grid>
      <Collapse in={expanded}>
        <Box display='flex' flexDirection='column' width='100%'>
          {children}
          <Box display='flex' justifyContent='flex-end' mb={2}>
            <ClearApplyButtons
              clearHandler={clearHandler}
              applyHandler={applyHandler}
            />
          </Box>
        </Box>
      </Collapse>
    </>
  );

  return isOnPaper ? (
    <FiltersPaper>{filtersComponent}</FiltersPaper>
  ) : (
    filtersComponent
  );
};
