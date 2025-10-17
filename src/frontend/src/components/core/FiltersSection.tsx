import { Box, Collapse, Grid } from '@mui/material';
import Paper from '@mui/material/Paper';
import { FC, ReactElement, useState } from 'react';
import styled from 'styled-components';
import { ClearApplyButtons } from './ClearApplyButtons';

interface FiltersSectionProps {
  children: ReactElement | ReactElement[];
  clearHandler?: () => void;
  applyHandler?: () => void;
  isOnPaper?: boolean;
  withApplyClearButtons?: boolean;
}

const FiltersPaper = styled(Paper)`
  width: 100%;
  background-color: #fff;
  padding: 8px 44px;
`;

export const FiltersSection: FC<FiltersSectionProps> = ({
  children,
  clearHandler,
  applyHandler,
  isOnPaper = true,
  withApplyClearButtons = true,
}): ReactElement => {
  const [expanded] = useState(true);

  const filtersComponent = (
    <>
      {/* //TODO: hiding controlers for now */}
      <Grid container spacing={3} sx={{ alignItems: 'flex-end' }}>
        <Box
          sx={{
            pt: 4,
            pb: 4,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-start',
            width: '100%',
          }}
        >
          {/* <Button
            variant='text'
            color='primary'
            endIcon={expanded ? <ExpandLess /> : <ExpandMore />}
            onClick={() => setExpanded(!expanded)}
            data-cy='button-filters-expand'
          >
            {expanded ? t('HIDE FILTERS') : t('SHOW FILTERS')}
          </Button> */}
        </Box>
      </Grid>
      <Collapse in={expanded}>
        <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
          {children}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
            {withApplyClearButtons && (
              <ClearApplyButtons
                clearHandler={clearHandler}
                applyHandler={applyHandler}
              />
            )}
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
