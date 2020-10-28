import React, { useState } from 'react';
import SearchIcon from '@material-ui/icons/Search';
import styled from 'styled-components';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Tab,
  Tabs,
} from '@material-ui/core';
import { TabPanel } from '../TabPanel';
import { useDebounce } from '../../hooks/useDebounce';
import { useBusinessArea } from '../../hooks/useBusinessArea';
import {
  ProgramNode,
  useAllProgramsQuery,
  useHouseholdChoiceDataQuery,
} from '../../__generated__/graphql';
import { LookUpHouseholdFilters } from './LookUpHouseholdTable/LookUpHouseholdFilters';
import { LookUpHouseholdTable } from './LookUpHouseholdTable/LookUpHouseholdTable';
import { LookUpIndividualFilters } from './LookUpIndividualTable/LookUpIndividualFilters';
import { LookUpIndividualTable } from './LookUpIndividualTable/LookUpIndividualTable';

export const LookUpHouseholdIndividual = (): React.ReactElement => {
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);
  const [filterHousehold, setFilterHousehold] = useState({
    householdSize: { min: undefined, max: undefined },
  });
  const [filterIndividual, setFilterIndividual] = useState({
    sex: '',
    age: { min: undefined, max: undefined },
  });
  const debouncedFilterHousehold = useDebounce(filterHousehold, 500);
  const debouncedFilterIndividual = useDebounce(filterIndividual, 500);
  const businessArea = useBusinessArea();
  const { data, loading } = useAllProgramsQuery({
    variables: { businessArea },
  });
  const {
    data: choicesData,
    loading: choicesLoading,
  } = useHouseholdChoiceDataQuery({
    variables: { businessArea },
  });
  if (loading || choicesLoading) return null;

  const { allPrograms } = data;
  const programs = allPrograms.edges.map((edge) => edge.node);

  const LookUp = styled.div`
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 10px;
    border: 1.5px solid #043e91;
    border-radius: 5px;
    color: #033f91;
    font-size: 16px;
    text-align: center;
    padding: 25px;
    font-weight: 500;
    cursor: pointer;
  `;
  const MarginRightSpan = styled.span`
    margin-right: 5px;
  `;
  const DialogFooter = styled.div`
    padding: 12px 16px;
    margin: 0;
    border-top: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
    text-align: right;
  `;
  const DialogTitleWrapper = styled.div`
    border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
  `;

  const StyledTabs = styled(Tabs)`
    && {
      max-width: 500px;
    }
  `;

  return (
    <>
      <LookUp onClick={() => setLookUpDialogOpen(true)}>
        <MarginRightSpan>
          <SearchIcon />
        </MarginRightSpan>
        <span>Look up Household / Individual</span>
      </LookUp>
      <Dialog
        maxWidth='lg'
        fullWidth
        open={lookUpDialogOpen}
        onClose={() => setLookUpDialogOpen(false)}
        scroll='paper'
        aria-labelledby='form-dialog-title'
      >
        <DialogTitleWrapper>
          <DialogTitle id='scroll-dialog-title'>
            <StyledTabs
              value={selectedTab}
              onChange={(event: React.ChangeEvent<{}>, newValue: number) => {
                setSelectedTab(newValue);
              }}
              indicatorColor='primary'
              textColor='primary'
              variant='fullWidth'
              aria-label='look up tabs'
            >
              <Tab label='LOOK UP HOUSEHOLD' />
              <Tab label='LOOK UP INDIVIDUAL' />
            </StyledTabs>
          </DialogTitle>
        </DialogTitleWrapper>
        <DialogContent>
          <TabPanel value={selectedTab} index={0}>
            <LookUpHouseholdFilters
              programs={programs as ProgramNode[]}
              filter={debouncedFilterHousehold}
              onFilterChange={setFilterHousehold}
              choicesData={choicesData}
            />
            <LookUpHouseholdTable
              filter={debouncedFilterHousehold}
              businessArea={businessArea}
              choicesData={choicesData}
            />
          </TabPanel>
          <TabPanel value={selectedTab} index={1}>
            <LookUpIndividualFilters
              filter={debouncedFilterIndividual}
              onFilterChange={setFilterIndividual}
            />
            <LookUpIndividualTable
              filter={debouncedFilterIndividual}
              businessArea={businessArea}
            />
          </TabPanel>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setLookUpDialogOpen(false)}>CANCEL</Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => null}
              data-cy='button-submit'
            >
              SAVE
            </Button>
          </DialogActions>
        </DialogFooter>
      </Dialog>
    </>
  );
};
