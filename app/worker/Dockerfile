# Build stage: compile the worker with the .NET 10 SDK.
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build

WORKDIR /src

# Copy the project file first so dependency restore can be cached.
COPY Worker.csproj .

RUN dotnet restore Worker.csproj

# Copy the application source and publish a release build.
COPY . .

RUN dotnet publish Worker.csproj --configuration Release --output /app/publish --no-restore --no-self-contained

# Runtime stage: use the smaller .NET runtime image.
FROM mcr.microsoft.com/dotnet/runtime:10.0 AS final

WORKDIR /app

# Copy only the published application from the build stage.
COPY --from=build /app/publish .

# Run with the non-root user provided by official .NET Linux images.
USER app

ENTRYPOINT ["dotnet", "Worker.dll"]
