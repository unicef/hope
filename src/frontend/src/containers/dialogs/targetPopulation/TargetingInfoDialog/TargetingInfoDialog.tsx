import { Box, Dialog, DialogContent, IconButton } from '@mui/material';
import { Close } from '@mui/icons-material';
import type { ChangeEvent, ReactElement } from 'react';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import styled from 'styled-components';
import TargetingDiagramImage from '../../../../assets/TargetingDiagramImage.png';
import { TabPanel } from '@components/core/TabPanel';
import { FlexFieldTab } from './FlexFieldTab';
import { Tabs, Tab } from '@core/Tabs';
import { responsiveValue } from 'src/responsive';

const DialogWrapper = styled(Dialog)`
  && {
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
}: TargetingInfoDialogProps): ReactElement => {
  const { t } = useTranslation();
  const [selectedTab, setTab] = useState(0);
  const changeTab = (_event: ChangeEvent<object>, newValue: number): void => {
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
      slotProps={{
        paper: {
          sx: {
            width: responsiveValue('100%', 'auto'),
            maxWidth: responsiveValue('calc(100% - 32px)', 'fit-content'),
            m: responsiveValue('16px', '32px'),
          },
        },
      }}
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
      <DialogContent
        sx={{
          width: responsiveValue('100%', '900px'),
          height: responsiveValue('auto', '600px'),
        }}
      >
        <StyledTabPanel value={selectedTab} index={0}>
          <FlexFieldTab />
        </StyledTabPanel>
        <TabPanel value={selectedTab} index={1}>
          <Box
            component="img"
            src={TargetingDiagramImage}
            alt="diagram"
            sx={{
              display: 'block',
              width: responsiveValue('100%', '754px'),
              height: responsiveValue('auto', '525px'),
              margin: '0 auto',
              backgroundColor: '#f8f8f8',
              position: responsiveValue('static', 'absolute'),
              top: '50%',
              left: '50%',
              transform: responsiveValue('none', 'translate(-50%, -50%)'),
            }}
          />
        </TabPanel>
      </DialogContent>
    </DialogWrapper>
  );
};
