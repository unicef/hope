import { Box, Button, Collapse, Grid } from '@mui/material';
import Paper from '@mui/material/Paper';
import type { FC, ReactElement } from 'react';
import { useState } from 'react';
import styled from 'styled-components';
import { ClearApplyButtons } from './ClearApplyButtons';
import { ExpandLess, ExpandMore } from '@mui/icons-material';
import { t } from 'i18next';
import { responsiveValue, useIsMobile } from 'src/responsive';

interface FiltersSectionProps {
  children: ReactElement | ReactElement[];
  clearHandler?: () => void;
  applyHandler?: () => void;
  isOnPaper?: boolean;
  withApplyClearButtons?: boolean;
  withHideShowButton?: boolean;
  initialExpanded?: boolean;
}

const FiltersPaper = styled(Paper)`
  width: 100%;
  background-color: #fff;
`;

export const FiltersSection: FC<FiltersSectionProps> = ({
  children,
  clearHandler,
  applyHandler,
  isOnPaper = true,
  withApplyClearButtons = true,
  withHideShowButton = false,
  initialExpanded = true,
}): ReactElement => {
  const isMobile = useIsMobile();
  // On phones and tablets the filters take a whole screen, so they start
  // collapsed behind the show/hide toggle.
  const hasHideShowButton = withHideShowButton || isMobile;
  const [expanded, setExpanded] = useState(initialExpanded && !isMobile);

  const filtersComponent = (
    <>
      <Collapse in={expanded}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            width: '100%',
            pt: 4,
          }}
        >
          {children}
          {!hasHideShowButton && (
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
              {withApplyClearButtons && (
                <ClearApplyButtons
                  clearHandler={clearHandler}
                  applyHandler={applyHandler}
                />
              )}
            </Box>
          )}
        </Box>
      </Collapse>
      {hasHideShowButton && (
        <Grid container spacing={3} sx={{ alignItems: 'flex-end' }}>
          <Box
            sx={{
              pt: 4,
              pb: 4,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              width: '100%',
            }}
          >
            <Button
              variant="text"
              color="primary"
              endIcon={expanded ? <ExpandLess /> : <ExpandMore />}
              onClick={() => setExpanded(!expanded)}
              data-cy="button-filters-expand"
            >
              {expanded ? t('HIDE FILTERS') : t('SHOW FILTERS')}
            </Button>
            {expanded && withApplyClearButtons && (
              <ClearApplyButtons
                clearHandler={clearHandler}
                applyHandler={applyHandler}
              />
            )}
          </Box>
        </Grid>
      )}
    </>
  );
  return isOnPaper ? (
    <FiltersPaper sx={{ padding: responsiveValue('8px 16px', '8px 44px') }}>
      {filtersComponent}
    </FiltersPaper>
  ) : (
    filtersComponent
  );
};
