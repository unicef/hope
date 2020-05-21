import React, { useState } from 'react';
import {
  IconButton,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Typography,
  Tabs,
  Tab
} from '@material-ui/core';
import { Close } from '@material-ui/icons';
import styled from 'styled-components';
import { TabPanel } from '../../../components/TabPanel';

export interface FinalizeTargetPopulationPropTypes {
  open: boolean;
  setOpen: Function;
}

const DialogWrapper = styled(Dialog)`
  && {
    .MuiPaper-root {
      max-width: fit-content;
    }
  }
`

const DialogTitleWrapper = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const DialogDescription = styled.div`
  margin: 20px 0;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.54);
`;

const ImagePlaceholder = styled.div`
  width: 754px;
  height: 525px;
  background-color: #f8f8f8;
`

export function TargetingInfoDialog({
  open,
  setOpen,
}) {
  const [selectedTab, setTab] = useState(0);
  const changeTab = (event: React.ChangeEvent<{}>, newValue: number) => {
    setTab(newValue);
  };
  const HeaderTabs = (
    <Tabs
      value={selectedTab}
      onChange={changeTab}
      aria-label='tabs'
      indicatorColor='primary'
      textColor='primary'
    >
      <Tab label='Targeting Diagram' />
      <Tab label='Flex Field List' disabled/>
    </Tabs>
  )
  return (
    <DialogWrapper
      open={open}
      onClose={() => setOpen(false)}
      scroll='paper'
      aria-labelledby='form-dialog-title'
    >
      <DialogTitleWrapper id='scroll-dialog-title'>
        {HeaderTabs}
        <IconButton onClick={() => setOpen(false)} color="primary" aria-label="Close Information Modal">
          <Close />
        </IconButton>
      </DialogTitleWrapper>
      <DialogContent>
        <DialogDescription>
          <TabPanel value={selectedTab} index={0}>
            <ImagePlaceholder />
          </TabPanel>
          <TabPanel value={selectedTab} index={1}>
            <div>Flex list is going to be here</div>
          </TabPanel>
        </DialogDescription>
      </DialogContent>
    </DialogWrapper>
  );
}
