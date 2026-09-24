package com.randompass.history;

import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

@SpringBootApplication
public class HistoryServiceApplication {
    public static void main(String[] args) { SpringApplication.run(HistoryServiceApplication.class, args); }

    @RestController
    static class HistoryController {
        private final StringRedisTemplate redis;
        private final ObjectMapper mapper;
        HistoryController(StringRedisTemplate redis, ObjectMapper mapper) { this.redis = redis; this.mapper = mapper; }

        @GetMapping("/health") Map<String, String> health() { redis.hasKey("password_history"); return Map.of("status", "UP"); }
        @PostMapping("/log-password-generation")
        @ResponseStatus(HttpStatus.CREATED)
        Map<String, String> log(@RequestBody Map<String, Object> event) throws JsonProcessingException {
            if (!event.containsKey("user_id") || !event.containsKey("length") || !event.containsKey("source")) {
                throw new IllegalArgumentException("user_id, length, and source are required");
            }
            redis.opsForList().leftPush("password_history", mapper.writeValueAsString(event));
            return Map.of("message", "generation metadata logged");
        }

        @GetMapping("/history/{userId}")
        List<String> history(@PathVariable String userId) {
            return redis.opsForList().range("password_history", 0, -1).stream()
                .filter(event -> event.contains("\"user_id\":\"" + userId + "\""))
                .toList();
        }
    }
}
