#include <stdio.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <netinet/ip_icmp.h>
#include <netinet/ip.h>

#define BUFFER_SIZE 4096

u_int16_t
check_sum ( u_int16_t* buf, u_int32_t size ) {
    register u_int32_t sum = 0;
    for ( ; size > 1; size -= sizeof(u_int16_t) )
        sum += *buf++;
    if ( size > 0 ) sum += * (u_char*) buf;
    while (sum >> 16)
        sum = (sum & 0xffff) + (sum >> 16);
    return (u_int16_t)(~sum);
}

u_int32_t
get_timestamp () {
    timeval tv;
    gettimeofday(&tv, NULL);
    return (u_int32_t)((tv.tv_sec % 86400) * 1000.0 + tv.tv_usec / 1000.0);
}

bool
check_packet ( icmp* packet ) {
    u_int16_t packet_cksum = packet->icmp_cksum;
    packet->icmp_cksum = 0;
    bool result = (packet_cksum == check_sum((u_int16_t*)packet, sizeof(*packet)));
    packet->icmp_cksum = packet_cksum;
    return result;
}

int
main ( int argc, char *argv[] ) {
  if ( argc != 2 ) {
    printf("Usage: ./times <time_server_ip>\n");
    return 1;
  }

  sockaddr_in dest = {0};
  dest.sin_family = AF_INET;
  dest.sin_addr.s_addr = inet_addr(argv[1]);
  if (dest.sin_addr.s_addr == (unsigned)-1) {
    printf("IP is not valid\n");
    return 2;
  }

  int sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
  if ( sock < 0 ) {
      close(sock);
      printf("Unable to create socket\n");
      return 3;
  }

  struct timeval t_recv = {0};
  t_recv.tv_sec = 5;
  setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, (char *)&t_recv, sizeof(struct timeval));

  sockaddr_in src = {0};
  src.sin_family = AF_INET;

  if ( bind(sock, (sockaddr*)&src, sizeof(src)) < 0 ) {
      close(sock);
      printf("Unable to open socket\n");
      return 4;
  }
  
  icmp out = {0};
  out.icmp_type = 13;
  out.icmp_id = getpid();
  out.icmp_otime = htonl(get_timestamp());
  out.icmp_cksum = check_sum((u_int16_t*)&out, sizeof(out));

  if ( sendto(sock, &out, sizeof(out), 0, (sockaddr*)&dest, (socklen_t)(sizeof(dest))) != sizeof(out) ) {
      close(sock);
      printf("Unable to send icmp request\n");
      return 5;
  }
  
  ip* ip_resp = NULL;
  icmp* icmp_resp = NULL;
  char buf[BUFFER_SIZE];
  do {
      ssize_t recv_bytes = recvfrom(sock, buf, BUFFER_SIZE, -1, NULL, NULL);
      if (recv_bytes < 0) {
          printf("Can't connect to server\n");
          return 7;
      }
      ip_resp = (ip*)buf;
      icmp_resp = (icmp*)(buf + (ip_resp->ip_hl << 2));
  } while ( icmp_resp->icmp_type != 14 );
  close(sock);

  if ( !check_packet(icmp_resp) ) {
      printf("Corrupted response\n");
      return 6;
  }

  printf("Originate: %d ms\nReceive: %d ms\nTransmit: %d ms\n",
          ntohl(icmp_resp->icmp_otime),
          ntohl(icmp_resp->icmp_rtime),
          ntohl(icmp_resp->icmp_ttime));

  printf("\nDelta: %d ms\n", ntohl(icmp_resp->icmp_otime) - ntohl(icmp_resp->icmp_ttime));
  return 0;
}
