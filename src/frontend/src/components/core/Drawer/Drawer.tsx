import { useBackendVersion } from '@hooks/useBackendVersion';
import { useBaseUrl } from '@hooks/useBaseUrl';
import { useFrontendVersion } from '@hooks/useFrontendVersion';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import { Box, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import Divider from '@mui/material/Divider';
import MUIDrawer from '@mui/material/Drawer';
import IconButton from '@mui/material/IconButton';
import List from '@mui/material/List';
import { ReactElement, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useProgramContext } from 'src/programContext';
import styled from 'styled-components';
import { AlertDialog } from '../AlertDialog';
import { Logo } from '../Logo';
import { DrawerItems } from './DrawerItems';
import { resourcesItems } from './menuItems';
import { ProgramStatusEnum } from '@restgenerated/models/ProgramStatusEnum';

const matchColorToWindowOrigin = (): string => {
  const url = window.location.href;
  if (window.location.hostname === 'localhost') {
    return '#A1E4B6';
  }
  if (url.includes('trn')) {
    return '#BF360C';
  }
  if (url.includes('stg')) {
    return '#673AB7';
  }
  if (url.includes('dev')) {
    return '#00796B';
  }
  if (url.includes('eph')) {
    return '#CC00EF';
  }
  if (url.includes('tst')) {
    return '#EF00A7';
  }
  return '#00ADEF';
};

const ToolbarHeader = styled('div')`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-left: 51px;
  background-color: ${matchColorToWindowOrigin()};
  color: white;
  box-shadow:
    0px 2px 4px 0px rgba(0, 0, 0, 0.2),
    0px 4px 5px 0px rgba(0, 0, 0, 0.14),
    0px 1px 10px 0px rgba(0, 0, 0, 0.12);
  min-height: 64px;
`;

interface DrawerComponentProps {
  open: boolean;
}

const DrawerComponent = styled(MUIDrawer)<DrawerComponentProps>`
  .MuiDrawer-paper {
    background-color: white;
    height: 100vh;
    position: relative;
    white-space: nowrap;
    width: ${(props) => (props.open ? '270px' : '55px')};
    transition:
      width 225ms cubic-bezier(0, 0, 0.2, 1) 0ms,
      width 195ms cubic-bezier(0, 0, 0.2, 1) 0ms;
    border-width: 0;
    overflow-x: hidden;
  }
`;

const CollapseIconButton = styled(IconButton)`
  color: #fff;
  opacity: 0.54;
`;

export const StyledLink = styled.a`
  color: #233944;
  font-size: 14px;
  font-weight: 500;
  line-height: 16px;
  text-decoration: none;
`;

const ResourcesText = styled('p')`
  text-align: left;
  font-size: 14px;
  color: #aaa;
  margin-left: 16px;
`;

const ToolbarScrollBox = styled(Box)`
  overflow-y: auto;
  max-height: calc(100vh - 64px);
  height: 100%;
`;

const Version = styled('div')`
  color: #aaa;
  padding: 4px;
  text-align: center;
  font-size: 14px;
`;

const Text = styled(ListItemText)`
  .MuiTypography-body1 {
    color: #233944;
    font-size: 14px;
    font-weight: 500;
    line-height: 16px;
  }
`;
const ProgramNotActiveBar = styled.div`
  background-color: #ff80ff;
  color: #721c24;
  border-radius: 5px;
  text-align: center;
  font-weight: 600;
`;

const Icon = styled(ListItemIcon)`
  && {
    min-width: 40px;
  }
`;

interface DrawerProps {
  open: boolean;
  handleDrawerClose: () => void;
  currentLocation: string;
  dataCy: string;
}

export const Drawer = ({
  open,
  handleDrawerClose,
  currentLocation,
  dataCy,
}: DrawerProps): ReactElement => {
  const { t } = useTranslation();
  const [showMismatchedDialog, setShowMismatchedDialog] = useState(false);
  const { selectedProgram } = useProgramContext();
  const { isAllPrograms } = useBaseUrl();

  const backendVersion = useBackendVersion();
  const frontendVersion = useFrontendVersion();

  useEffect(() => {
    if (
      !showMismatchedDialog &&
      backendVersion &&
      frontendVersion &&
      backendVersion !== frontendVersion
    ) {
      setShowMismatchedDialog(true);
    }
  }, [backendVersion, frontendVersion, showMismatchedDialog]);

  let notActiveBar = null;
  const programStatus = selectedProgram?.status;
  const isActive = programStatus === ProgramStatusEnum.ACTIVE;
  const isDefined = programStatus !== undefined && programStatus !== null;
  if (!isAllPrograms && !isActive && isDefined) {
    notActiveBar = (
      <ProgramNotActiveBar data-cy="program-inactive-subheader">
        Programme Inactive
      </ProgramNotActiveBar>
    );
  }

  return (
    <DrawerComponent
      variant="permanent"
      open={open}
      style={{ height: '100vh' }}
      data-cy={dataCy}
    >
      <ToolbarHeader>
        <Logo
          transparent={matchColorToWindowOrigin() !== '#00ADEF'}
          displayLogoWithoutSubtitle
        />
        <CollapseIconButton onClick={handleDrawerClose}>
          <ChevronLeftIcon />
        </CollapseIconButton>
      </ToolbarHeader>
      {notActiveBar}
      <Divider />
      <ToolbarScrollBox>
        <List>
          <DrawerItems open={open} currentLocation={currentLocation} />
        </List>
        <Box mb={2}>
          <Divider />
        </Box>
        {open && (
          <Box mb={2}>
            <ResourcesText>{t('Resources')}</ResourcesText>
          </Box>
        )}
        {resourcesItems.map((item) => (
          <ListItem key={item.name + item.href}>
            <StyledLink
              data-cy={`nav-resources-${item.name}`}
              target="_blank"
              href={item.href}
            >
              <Box display="flex">
                <Icon>{item.icon}</Icon>
                <Text primary={item.name} />
              </Box>
            </StyledLink>
          </ListItem>
        ))}
        {open && <Version>Version: {frontendVersion}</Version>}
      </ToolbarScrollBox>
      <AlertDialog
        show={showMismatchedDialog}
        message={t('Version mismatch, please refresh page')}
      />
    </DrawerComponent>
  );
};
