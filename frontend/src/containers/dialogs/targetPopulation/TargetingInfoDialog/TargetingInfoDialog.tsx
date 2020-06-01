import React, { useState } from 'react';
import {
  IconButton,
  Dialog,
  DialogContent,
  Tabs,
  Tab
} from '@material-ui/core';
import { Close } from '@material-ui/icons';
import styled from 'styled-components';
import { TabPanel } from '../../../../components/TabPanel';
import { FlexFieldTab } from './FlexFieldTab';
import TargetingDiagramImage from '../../../../assets/TargetingDiagramImage.png';

export interface FinalizeTargetPopulationPropTypes {
  open: boolean;
  setOpen: Function;
}

const DialogWrapper = styled(Dialog)`
  && {
    .MuiPaper-root {
      max-width: fit-content;
    }
    .MuiDialogContent-root {
      padding: 0;
    }
  }
`

const DialogTitleWrapper = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid ${({ theme }) => theme.hctPalette.lighterGray};
`;

const StyledDialogContent = styled(DialogContent)`
  width: 900px;
  height: 600px;
`;

const TargetingDiagram = styled.img`
  width: 754px;
  height: 525px;
  margin: 0 auto;
  background-color: #f8f8f8;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
`;

const StyledTabPanel = styled(TabPanel)`
  && {
    height: 100%;
  }
`;

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
      <Tab label='Flex Field List' />
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
      <StyledDialogContent>
        <StyledTabPanel value={selectedTab} index={0}>
          <TargetingDiagram src={TargetingDiagramImage} alt="diagram"/>
        </StyledTabPanel>
        <TabPanel value={selectedTab} index={1}>
          <FlexFieldTab />
        </TabPanel>
      </StyledDialogContent>
    </DialogWrapper>
  );
}
