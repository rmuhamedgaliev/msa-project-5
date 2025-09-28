FROM openjdk:24-slim
WORKDIR .
COPY build/libs/*.jar app.jar
ENTRYPOINT ["java","-jar","/app.jar"]