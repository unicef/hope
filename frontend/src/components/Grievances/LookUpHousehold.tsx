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

export const LookUpHousehold = (): React.ReactElement => {
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

  const DialogContainer = styled.div`
    width: 700px;
  `;

  const StyledTabs = styled(Tabs)`
    && {
      max-width: 500px;
    }
  `;
  const [lookUpDialogOpen, setLookUpDialogOpen] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);

  return (
    <>
      <LookUp onClick={() => setLookUpDialogOpen(true)}>
        <MarginRightSpan>
          <SearchIcon />
        </MarginRightSpan>
        <span>Look up Household</span>
      </LookUp>
      <Dialog
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
          <DialogContainer>
            <TabPanel value={selectedTab} index={0}>
              households
            </TabPanel>
            <TabPanel value={selectedTab} index={1}>
              individuals
            </TabPanel>
          </DialogContainer>
        </DialogContent>
        <DialogFooter>
          <DialogActions>
            <Button onClick={() => setLookUpDialogOpen(false)}>CANCEL</Button>
            <Button
              type='submit'
              color='primary'
              variant='contained'
              onClick={() => console.log('lookup')}
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
