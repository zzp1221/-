FROM eclipse-temurin:21-jre

WORKDIR /app

RUN mkdir -p /app/logs /data/sandbox-temp

COPY target/zhixue-control-plane-0.0.1-SNAPSHOT.jar /app/app.jar

EXPOSE 8081

ENTRYPOINT ["java", "-jar", "/app/app.jar"]
