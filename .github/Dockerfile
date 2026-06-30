FROM rust:1.88.0-trixie AS builder

WORKDIR /app
COPY . .
RUN cargo build --release --bin simeis-server --no-default-features --features tokio

FROM debian:trixie-slim

WORKDIR /app
COPY --from=builder /app/target/release/simeis-server .

EXPOSE 8081

CMD ["./simeis-server"]
