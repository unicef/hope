import { Dialog, DialogContent, IconButton } from '@mui/material';
import { Close } from '@mui/icons-material';
import * as React from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import TargetingDiagramImage from '../../../../assets/TargetingDiagramImage.png';
import { TabPanel } from '@components/core/TabPanel';
import { FlexFieldTab } from './FlexFieldTab';
import { Tabs, Tab } from '@core/Tabs';

const DialogWrapper = styled(Dialog)`
  && {
    .MuiPaper-root {
      max-width: fit-content;
    }
    .MuiDialogContent-root {
      padding: 0;
    }
  }
`;

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

export interface TargetingInfoDialogProps {
  open: boolean;
  setOpen: (open: boolean) => void;
}

export const TargetingInfoDialog = ({
  open,
  setOpen,
}: TargetingInfoDialogProps): React.ReactElement => {
  const { t } = useTranslation();
  const [selectedTab, setTab] = useState(0);
  const changeTab = (
    _event: React.ChangeEvent<object>,
    newValue: number,
  ): void => {
    setTab(newValue);
  };
  const HeaderTabs = (
    <Tabs
      value={selectedTab}
      onChange={changeTab}
      aria-label="tabs"
      indicatorColor="primary"
      textColor="primary"
    >
      <Tab data-cy="tab-field-list" label={t('Field List')} />
      <Tab data-cy="tab-targeting-diagram" label={t('Targeting Diagram')} />
    </Tabs>
  );
  return (
    <DialogWrapper
      open={open}
      onClose={() => setOpen(false)}
      scroll="paper"
      aria-labelledby="form-dialog-title"
    >
      <DialogTitleWrapper>
        {HeaderTabs}
        <IconButton
          onClick={() => setOpen(false)}
          color="primary"
          aria-label="Close Information Modal"
          data-cy="button-close"
        >
          <Close />
        </IconButton>
      </DialogTitleWrapper>
      <StyledDialogContent>
        <StyledTabPanel value={selectedTab} index={0}>
          <FlexFieldTab />
        </StyledTabPanel>
        <TabPanel value={selectedTab} index={1}>
          <TargetingDiagram src={TargetingDiagramImage} alt="diagram" />
        </TabPanel>
      </StyledDialogContent>
    </DialogWrapper>
  );
};
