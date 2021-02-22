//@flow
import React from 'react';
import styled from 'styled-components';
import { fontSize, fontWeight } from '@scality/core-ui/dist/style/theme';

const DashboardPageContainer = styled.div`
  display: flex;
  flex-wrap: wrap;
  height: 100%;
  overflow: auto;
  margin-right: 8px;
`;

const LeftContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 51%;
  min-width: 678px;
  flex: 1;
  margin-left: 8px;
`;

const RightMetricsContainer = styled.div`
  display: flex;
  flex-wrap: nowrap;
  width: 49%;
  min-width: 670px;
  // 100vh - 48px(navbar) - 8px(margin-bottom)
  height: calc(100vh - 56px);
  margin: 0 0 8px 8px;
  flex: 1;
`;

const GlobalHealthCard = styled.div`
  height: 160px;
  background-color: ${(props) => props.theme.brand.primary};
  margin-bottom: 8px;
`;

const InventoryCard = styled.div`
  height: 156px;
  background-color: ${(props) => props.theme.brand.primary};
`;

const AlertActivityCard = styled.div`
  // 100vh - 48px(navbar) - 160px(global health) - 24px(3 * 8px) - 156px(inventory)
  height: calc(100vh - 388px);
  background-color: ${(props) => props.theme.brand.primary};
  margin-top: 8px;
`;

const ServiceCard = styled.div`
  // 100vh - 48px(navbar) - 160px(global health) - 16px(2 * 8px)
  height: calc(100vh - 224px);
  width: 50%;
  background-color: ${(props) => props.theme.brand.primary};
  margin-left: 8px;
  margin-bottom: 8px;
`;

const NetworkCard = styled.div`
  width: 50%;
  background-color: ${(props) => props.theme.brand.primary};
`;

const MetricsCard = styled.div`
  width: 50%;
  background-color: ${(props) => props.theme.brand.primary};
  margin-left: 8px;
`;

const GlobalUnderLeft = styled.div`
  width: 50%;
  margin-bottom: 8px;
`;

const CardTitle = styled.div`
  color: ${(props) => props.theme.brand.textPrimary};
  padding: 16px 0 0 16px;
  font-weight: ${fontWeight.bold};
  font-size: ${fontSize.large};
`;

const DashboardPage = (props: Object) => {
  return (
    <DashboardPageContainer>
      <LeftContainer>
        <GlobalHealthCard>
          <CardTitle>Global Health</CardTitle>
        </GlobalHealthCard>
        <div style={{ display: 'flex', width: '100%' }}>
          <GlobalUnderLeft>
            <InventoryCard>
              <CardTitle>Inventory</CardTitle>
            </InventoryCard>
            <AlertActivityCard>
              <CardTitle>Alerts</CardTitle>
            </AlertActivityCard>
          </GlobalUnderLeft>
          <ServiceCard>
            <CardTitle>Services</CardTitle>
          </ServiceCard>
        </div>
      </LeftContainer>
      <RightMetricsContainer>
        <NetworkCard>
          <CardTitle>Network</CardTitle>
        </NetworkCard>
        <MetricsCard>
          <CardTitle>Metrics</CardTitle>
        </MetricsCard>
      </RightMetricsContainer>
    </DashboardPageContainer>
  );
};
export default DashboardPage;
