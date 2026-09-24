targetScope = 'resourceGroup'

param location string
param managedEnvironmentResourceId string
param registryServer string
param pullIdentityResourceId string
param images object
param releaseId string
@allowed(['55', '56', '57', '58', '59', '60'])
param projectNumber string
param projectName string
param apiPort int
param webPort int
param apiHealthPath string
param webApiEnvironmentVariable string
param apiEnvironment object = {}

var apiAppName = 'p10-p${projectNumber}-api'
var webAppName = 'p10-p${projectNumber}-web'
var commonTags = {
  owner: 'Path-AI-Engineer'
  roadmap: 'plan-10'
  project: projectName
  release: releaseId
  costProfile: 'consumption-scale-to-zero'
  persistence: 'ephemeral-demo'
}
var workloadIdentity = {
  type: 'UserAssigned'
  userAssignedIdentities: {
    '${pullIdentityResourceId}': {}
  }
}
var registryCredentials = [
  {
    server: registryServer
    identity: pullIdentityResourceId
  }
]

resource api 'Microsoft.App/containerApps@2024-03-01' = {
  name: apiAppName
  location: location
  tags: commonTags
  identity: workloadIdentity
  properties: {
    managedEnvironmentId: managedEnvironmentResourceId
    configuration: {
      activeRevisionsMode: 'Single'
      registries: registryCredentials
      ingress: {
        external: true
        targetPort: apiPort
        transport: 'auto'
        allowInsecure: false
      }
    }
    template: {
      containers: [
        {
          name: 'api'
          image: images.api
          env: [for setting in items(apiEnvironment): {
            name: setting.key
            value: string(setting.value)
          }]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          probes: [
            {
              type: 'Liveness'
              httpGet: { path: apiHealthPath, port: apiPort }
              initialDelaySeconds: 20
              periodSeconds: 20
            }
            {
              type: 'Readiness'
              httpGet: { path: apiHealthPath, port: apiPort }
              initialDelaySeconds: 10
              periodSeconds: 10
            }
          ]
        }
      ]
      scale: { minReplicas: 0, maxReplicas: 1 }
    }
  }
}

resource web 'Microsoft.App/containerApps@2024-03-01' = {
  name: webAppName
  location: location
  tags: commonTags
  identity: workloadIdentity
  properties: {
    managedEnvironmentId: managedEnvironmentResourceId
    configuration: {
      activeRevisionsMode: 'Single'
      registries: registryCredentials
      ingress: {
        external: true
        targetPort: webPort
        transport: 'auto'
        allowInsecure: false
      }
    }
    template: {
      containers: [
        {
          name: 'web'
          image: images.web
          env: [
            {
              name: webApiEnvironmentVariable
              value: 'https://${api.properties.configuration.ingress.fqdn}'
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: { minReplicas: 0, maxReplicas: 1 }
    }
  }
}

output endpoints object = {
  webUrl: 'https://${web.properties.configuration.ingress.fqdn}'
  apiUrl: 'https://${api.properties.configuration.ingress.fqdn}'
  swaggerUrl: 'https://${api.properties.configuration.ingress.fqdn}/docs'
  openApiUrl: 'https://${api.properties.configuration.ingress.fqdn}/openapi.json'
}

output costBoundary object = {
  managedEnvironmentCreated: false
  registryCreated: false
  databaseCreated: false
  persistentStorageCreated: false
  publicApplications: 2
  minReplicas: 0
  maxReplicasPerApplication: 1
  persistence: 'ephemeral; state resets on scale-down or replacement'
}
